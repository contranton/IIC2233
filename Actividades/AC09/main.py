"""
-- main.py --

Este módulo cuenta con tres clases:
- Tarea,
- Programador,
- Administrador.
"""

from itertools import count
from collections import deque
from random import randint, random
import threading
import time


TOTAL = 8 * 60 * 60  # segundos de simulación --> ocho horas
VELOCIDAD = 3600     # rapidez según el tiempo de simulación

# Esta simple función te permite simular minutos de trabajo.
reloj = lambda minutos: time.sleep(minutos * 60 / VELOCIDAD)

# Definicion del sistema global de recepcion de tareas
sistema_tareas_lock = threading.Lock()
sistema = []

# Calculo del tiempo de simulacion para los prints
tiempo_inicial = 0
sim_time = lambda: int((time.time() - tiempo_inicial)* VELOCIDAD / 60)

class Tarea:
    """
    Pequeña clase que modela una tarea.
    """

    id_iter = count(1)

    def __init__(self):
        """
        Inicializa una nueva tarea.
        Le asigna un identificador, un estado de completitud y una duración.
        """

        self.id_ = next(Tarea.id_iter)
        self._hecho = 0
        self.duracion = randint(30, 120)

    def avanzar(self):
        """
        Permite desarrollar una unidad de trabajo de la tarea.
        Retorna un booleano que indica si la tarea está lista.
        """

        self._hecho += 1
        return self._hecho == self.duracion

    def __repr__(self):
        return f'T{self.id_} [{self._hecho}/{self.duracion}]'


class Programador(threading.Thread):
    """
    Pequeña clase que modela un programador.
    """

    def __init__(self, nombre, at_work_event):
        super().__init__()
        self.nombre = nombre

        self.tareas_asignadas = deque()
        self.lento = True if random() < 0.3 else False

        self.at_work_event = at_work_event
        self.daemon = True

    @property
    def can_work(self):
        return not self.at_work_event.is_set()

    def run(self):
        # Aunque haya terminado todas sus tareas, no puede irse del trabajo!
        while self.can_work:
            if self.tareas_asignadas:
                tarea = self.tareas_asignadas.popleft()
                self.trabajar_en_tarea(tarea)
                self.enviar_tarea(tarea)

    def trabajar_en_tarea(self, tarea):
        while self.can_work:
            reloj(1)
            if self.lento:
                if random() < 0.4:
                    continue
            else:
                if random() < 0.1:
                    continue
            if tarea.avanzar():
                print("({}) {}: He terminado la tarea {}"
                      .format(sim_time(), self.nombre, tarea.id_))
                break

    def enviar_tarea(self, tarea):
        with sistema_tareas_lock:
            reloj(20) if self.lento else reloj(5)
            if self.can_work:
                print("({}) {}: He entregado la tarea {}"
                      .format(sim_time(), self.nombre, tarea.id_))
                sistema.append(tarea)

    def get_tareas_restantes(self):
        return len(self.tareas_asignadas)


class Administrador:
    """
    Pequeña clase que modela un administrador.
    """

    def __init__(self, programadores):
        self.programadores = programadores

    def sort_progs(self):
        return sorted(self.programadores,
                      key=lambda p: p.get_tareas_restantes())

    def repartir_nueva_tarea(self):
        reloj(randint(10, 15))
        chosen_prog = self.sort_progs()[0]
        tarea = Tarea()
        chosen_prog.tareas_asignadas.append(tarea)
        print("({}) Nueva tarea de id={} de {} minutos para {}"
              .format(sim_time(), tarea.id_,
                      tarea.duracion, chosen_prog.nombre))

    def repartir_tareas_iniciales(self):
        for p in self.programadores:
            tarea = Tarea()
            print("({}) Nueva tarea de id={} de {} minutos para {}"
              .format(sim_time(), tarea.id_,
                      tarea.duracion, p.nombre))
            p.tareas_asignadas.append(tarea)


if __name__ == '__main__':
    # Aquí tienes una lista con ocho nombres para los programadores.
    # No hay un bonus por reconocer cuál es la temática entre ellos.

    nombres = [
        'Alex',
        'Matt',
        'Jamie',
        'Nick',
        'Nebil',
        'Belén',
        'Cristian',
        'Jaime',
    ]

    # Aquí deberías escribir unas pocas líneas de código.
    # Hmmm... por ejemplo, crear las instancias en juego.
    # ###################################################
    at_work_event = threading.Event()

    programadores = [Programador(n, at_work_event) for n in nombres]
    admin = Administrador(programadores)

    # ###################################################

    # Start threads -- They'll do nothing at first
    # Lo hago despues de setear tiempo_inicial para
    # incluir prints del tiempo ;)
    [p.start() for p in programadores]
    tiempo_inicial = time.time()
    admin.repartir_tareas_iniciales()

    while time.time() - tiempo_inicial < (TOTAL / VELOCIDAD):
        # Aquí comienza la simulación síncrona.
        # Deberías escribir algo de código acá.
        # (Recuerda borrar el pass, obviamente)
        # #####################################
        admin.repartir_nueva_tarea()

        # #####################################

    # Una vez terminado el tiempo, activar evento que apaga a los trabajadores
    at_work_event.set()

    print('Fin de simulación.')
    print(sorted(sistema, key=lambda t: t.id_))
    input()
