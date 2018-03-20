from collections import namedtuple
from datetime import datetime
from random import randint

from razas import MaestroRaza, AprendizRaza, AsesinoRaza


def _planet_defaults():
    """
    Returns the default values for a planet other than
    its name, race, and parent galaxy, which are user-specified.
    """
    planet = namedtuple("TupPlaneta",
                        "nombre raza ultima_recoleccion soldados magos\
                        conquistado nivel_ataque nivel_economia torre\
                        cuartel tasa_minerales tasa_deuterio galaxia")
    return planet(nombre="UNSET",
                  raza="UNSET",
                  galaxia="UNSET",
                  ultima_recoleccion=datetime.now(),
                  soldados=0,
                  magos=0,
                  conquistado=False,
                  nivel_ataque=0,
                  nivel_economia=0,
                  torre=False,
                  cuartel=False,
                  tasa_minerales=randint(1, 10),
                  tasa_deuterio=randint(5, 15))


class Planeta(object):
    """Documentation for Planeta

    """
    def __init__(self, PlanetNamedTuple=_planet_defaults()):
        super(Planeta, self).__init__()

        print(PlanetNamedTuple)
        # Genera atributos de la clase en base a aquellos definidos
        # en la base de datos. Es redundante haber creado un NamedTuple
        # al inicio?
        for key, value in PlanetNamedTuple._asdict().items():
            print(type(key), type(value))
            setattr(self, key, value)
        
    @property
    def raza(self):
        return self._raza

    @raza.setter
    def _(self, raza_str):
        self._raza = {"Maestro": MaestroRaza,
                      "Aprendiz": AprendizRaza,
                      "Asesino": AsesinoRaza}[raza_str]

            
    @property
    def soldados(self):
        return self._soldados

    @soldados.setter
    def _(self, value):
        max_soldados = self.raza.max_pop - self.magos
        self._soldados = min(max(value, 0), max_soldados)

    @property
    def tasa_minerales(self):
        lvl = self.nivel_economia
        multiplier = {0: 1, 1: 1.2, 2: 1.5, 3: 2}  # Level: Multiplier
        return self._tasa_minerales * multiplier[lvl]

    @tasa_minerales.setter
    def _(self, valor):
        self._tasa_minerales = valor

    @property
    def tasa_deuterio(self):
        lvl = self.nivel_economia
        multiplier = {0: 1, 1: 1.2, 2: 1.5, 3: 2}  # Level: Multiplier
        return self._tasa_deuterio * multiplier[lvl]

    @tasa_deuterio.setter
    def _(self, valor):
        self._tasa_deuterio = valor

    @property
    def evolucion(self):
        return self.nivel_economia + self.nivel_ataque\
            + (self.soldados + self.magos)/(self.raza.max_pop)\
            + int(self.torre) + int(self.cuartel)
        
class Galaxia(object):
    """Documentation for Galaxia

    """
    def __init__(self, nombre, planetas):
        super(Galaxia, self).__init__()
        self.nombre = nombre
        self.planetas = planetas


if __name__ == '__main__':
    p = Planeta()
