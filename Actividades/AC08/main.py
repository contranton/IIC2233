import csv
import statistics
from functools import reduce
from random import expovariate, sample, random, uniform


class Persona:
    def __init__(self, nombre, sexo):
        self.nombre = nombre
        self.sexo = sexo
        self.d_recorrida = 0
        self.activo = True
        self.velocidad = 0
        self.probabilidad_lesion = 0

    @property
    def tiempo_llegada(self):
        return max((42000 - self.d_recorrida)/self.velocidad, 0)

    @property
    def tiempo_mitad(self):
        return max((21000 - self.d_recorrida)/self.velocidad, 0)

    def upd_distance(self, time_delta):
        self.d_recorrida += self.velocidad*time_delta
    
    def __repr__(self):
        s = "Persona({}, {}, {})"
        return s.format(self.nombre, self.sexo, self.__class__.__name__)


class Amateur(Persona):
    def __init__(self, nombre, sexo):
        super().__init__(nombre,sexo)
        self.velocidad = uniform(1.4*60, 2.8*60)
        self.probabilidad_lesion = 0.4


class Aficionado(Persona):
    def __init__(self, nombre, sexo):
        super().__init__(nombre,sexo)
        self.velocidad = uniform(2.8*60, 4.2*60)
        self.probabilidad_lesion = 0.25


class Profesional(Persona):
    def __init__(self, nombre, sexo):
        super().__init__(nombre,sexo)
        self.velocidad = uniform(4.2*60, 5.7*60)
        self.probabilidad_lesion = 0.15


class Evento(object):
    def __init__(self, nombre, tiempo, persona=None):
        self.nombre = nombre
        self.persona = persona
        if callable(tiempo):
            self.tiempo_actualizado = tiempo
        else:
            self.tiempo_actualizado = lambda p: tiempo
        self._tiempo = tiempo

    @property
    def tiempo(self):
        return self.tiempo_actualizado(self.persona)

    def __repr__(self):
        s = "Evento({}, {}, {})"
        return s.format(self.nombre, self.tiempo, self.persona)


class Simulacion(object):
    def __init__(self, it, do_print=False):
        if do_print:
            print("Iteracion | Tiempo de evento (segundos) | Descripcion de evento | Entidad afectada")
        self.iteracion = it
        self.do_print = do_print

        self.tiempo = 0
        self.activos = self.read_personas()
        self.inactivos = []

        self.eventos = [Evento("llegada",
                               lambda p: self.tiempo + p.tiempo_llegada,
                               persona)
                        for persona in self.activos]

        self.eventos += [Evento("accidente", expovariate(1/25)),
                         Evento("lluvia_start", expovariate(1/300))]
        self.funciones = {"atajo": self.atajo,
                          "accidente": self.accidente,
                          "lluvia_start": self.lluvia_start,
                          "lluvia_end": self.lluvia_end,
                          "llegada": self.llegada}
        self.tiempos_llegada = []

    def atajo(self, evento):
        p = evento.persona
        p.d_recorrida += 4
        self.log("corredor toma atajo", p.title())

    def lluvia_start(self, evento):
        for p in self.activos:
            p.velocidad *= 3/4
        self.log("inicio lluvia", "simulacion")

        self.eventos.append(Evento("lluvia_end", self.tiempo + 30))

    def lluvia_end(self, evento):
        for p in self.activos:
            p.velocidad *= 4/3
        self.log("fin lluvia", "simulacion")

    def llegada(self, evento):
        p = evento.persona
        tiempo_llegada = evento.tiempo
        self.log("corredor llega a la meta", p.nombre)
        self.tiempos_llegada.append((tiempo_llegada, p))
            
    def accidente(self, evento):
        chosen = sample(self.activos, min(5, len(self.activos)))
        for p in chosen:
            if random() < p.probabilidad_lesion:
                self.log("corredor sufre accidente", p.nombre)
                p.activa = False
                self.activos.remove(p)
                self.inactivos.append(p)

        self.eventos.append(
            Evento("accidente", self.tiempo + expovariate(1/25))
        )

    def run(self):
        last_time = 0
        while self.eventos and self.activos and self.tiempo < 8*60:
            self.eventos.sort(key=lambda e: e.tiempo)
            for p in self.activos:
                p.upd_distance(self.tiempo - last_time)
            evento = self.eventos.pop(0)
            last_time = self.tiempo
            self.tiempo = evento.tiempo
            self.funciones[evento.nombre](evento)

    def log(self, descripcion, entidad):
        if self.do_print:
            print("{} | {} | {} | {}"
                  .format(self.iteracion,
                          int(self.tiempo),
                          descripcion,
                          entidad))
            
    def read_personas(self):
        personas = []
        with open("competidores.csv", 'r', encoding="utf-8") as f:
            reader = csv.reader(f, delimiter=",")
            for line in reader:
                categoria = line[3]
                categorias = {"amateur": Amateur,
                              "aficionado": Aficionado,
                              "profesional": Profesional}
                persona = categorias[categoria](line[1], line[2])
                personas.append(persona)
        return personas


class Estadisticas:
    def __init__(self, competidores_end):
        self.iteraciones = len(competidores_end)
        self.terminaron = list(map(lambda x: len(x), competidores_end))
        self.terminaron = sum(self.terminaron)/self.iteraciones
        self.competidores_end = reduce(lambda x,y: x+y, competidores_end)
        self.wm = list(filter(lambda x: x[1].sexo=='femenino',competidores_end))
        self.mn = list(filter(lambda x: x[1].sexo=='masculino',competidores_end))
        self.amateurs_wm = list(filter(lambda x: isinstance(x[1], Amateur),
        self.wm))
        self.aficioados_wm = list(filter(lambda x: isinstance(x[1], Aficionado),
        self.wm))
        self.pros_wm = list(filter(lambda x: isinstance(x[1], Profesional),
        self.wm))
        self.amateurs_mn = list(filter(lambda x: isinstance(x[1], Amateur),
        self.mn))
        self.aficioados_mn = list(filter(lambda x: isinstance(x[1], Aficionado),
        self.mn))
        self.pros_mn = list(filter(lambda x: isinstance(x[1], Profesional),
        self.mn))
        
    def tiempo_promedio(self, competidores):
        totales = [tup[0] for tup in competidores]
        tiempo_promedio = statistics.mean(totales)
        return tiempo_promedio

    def __str__(self):
        total_mean = self.tiempo_promedio(self.competidores_end)
        amateur_man = self.tiempo_promedio(self.amateur_mn)
        amateur_woman = self.tiempo_promedio(self.amateurs_wm)
        aficionado_man = self.tiempo_promedio(self.aficioados_mn)
        aficionado_woman = self.tiempo_promedio(self.aficionado_wm)
        pro_man = self.tiempo_promedio(self.pros_mn)
        pro_woman = self.tiempo_promedio(self.pros_wm)
        return ('Promedio que termino: {}'.format(self.terminaron)
        + 'Tiempo promedio de corredores en terminar carrera: {}'.format(
        total_mean)
        + 'Tiempo mujeres Amateur: {}'.format(amateur_woman)
        + 'Tiempo mujeres Aficionadas: {}'.format(aficionado_woman)
        + 'Tiempo mujeres Profesionales: {}'.format(pros_wm)
        + 'Tiempo hombres Amateur: {}'.format(amateur_man)
        + 'Tiempo hombres Aficionados: {}'.format(aficionado_man)
        + 'Tiempo hombres Profesionales: {}'.format(pro_man))
        


    
if __name__ == '__main__':
    sims = [Simulacion(i) for i in range(10)]
    [sim.run() for sim in sims]
    tiempos = [sim.tiempos_llegada for sim in sims]
    Estadisticas(tiempos)
