import csv
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
        return (42000 - self.d_recorrida)/self.velocidad

    @property
    def tiempo_mitad(self):
        return (21000 - self.d_recorrida)/self.velocidad

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
    def __init__(self):
        print("Iteracion | Tiempo de evento (segundos) | Descripcion de evento | Entidad afectada")
        self.iteracion = 0
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

        self.eventos.append(Evento("lluvia_end", self.tiempo + 30))

    def lluvia_end(self, evento):
        for p in self.activos:
            p.velocidad *= 4/3

    def llegada(self, evento):
        p = evento.persona
        tiempo_llegada = evento.tiempo

        self.tiempos_llegada.append((p.nombre, tiempo_llegada))
            
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
        while self.eventos and self.activos:
            self.eventos.sort(key=lambda e: e.tiempo)
            evento = self.eventos.pop(0)
            self.funciones[evento.nombre](evento)
            self.tiempo = evento.tiempo

    def log(self, descripcion, entidad):
        print("{} | {} | {} | {}"
              .format(self.iteracion,
                      int(self.tiempo*60),
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

if __name__ == '__main__':
    sim = Simulacion()
