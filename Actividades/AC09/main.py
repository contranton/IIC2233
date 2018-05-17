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

    def __init__(self, nombre):
        self.nombre = nombre

        self.tareas_asignadas = deque()
        self.lento = True if random() < 0.3 else False

        self.daemon = True

    def run(self):
        # Aunque haya terminado todas sus tareas, no puede irse del trabajo!
        while True:
            if self.tareas_asignadas:
                tarea = self.tareas_asignadas.popleft()
                self.trabajar_en_tarea(tarea)
                self.enviar_tarea(tarea)

    def trabajar_en_tarea(self, tarea):
        while True:
            reloj(1)
            if self.lento:
                if random() < 0.4:
                    continue
            else:
                if random() < 0.1:
                    continue
            if tarea.avanzar():
                print("{}: He terminado la tarea {}".format(self.nombre,
                                                            tarea.id_))
                return tarea

    def enviar_tarea(self, tarea):
        with sistema_tareas_lock:
            reloj(20) if self.lento else reloj(5)
            print("{}: He entregado la tarea {}".format(self.nombre,
                                                        self.id_))
            sistemas.append(tarea)

    def get_tareas_restantes(self):
        return len(self.tareas_asignadas)


class Administrador:
    """
    Pequeña clase que modela un administrador.
    """

    def repartir_tareas():
        while True:


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

    programadores = [Programador(n) for n in nombres]
    admin = Administrador(programadores)

    # ###################################################

    tiempo_inicial = time.time()
    while time.time() - tiempo_inicial < (TOTAL / VELOCIDAD):
        pass
        # Aquí comienza la simulación síncrona.
        # Deberías escribir algo de código acá.
        # (Recuerda borrar el pass, obviamente)
        # #####################################



        # #####################################

    print('Fin de simulación.')
