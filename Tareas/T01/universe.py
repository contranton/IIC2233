from datetime import datetime
from random import randint
from copy import deepcopy
from collections import namedtuple

from razas import MaestroRaza, AprendizRaza, AsesinoRaza
from fileio import read_planets, read_galaxies, write_csv
from colors import red, green

"""
Defines Planet, Galaxy, and Universe classes
"""
cost = namedtuple("Costo", "mins deut")

COSTO_CUARTEL = cost(200, 500)
VIDA_CUARTEL = 5000

COSTO_TORRE = cost(150, 300)
ATAQUE_TORRE = 1000
VIDA_TORRE = 2000

# Don't worry, these names don't conflict with the keywords
rate = namedtuple("Tasa", "min max")

TASA_MINS = rate(1, 10)
TASA_DEUT = rate(5, 15)


def _planet_defaults(nombre, raza, galaxia):
    """
    Returns the default values for a planet other than
    its name, race, and parent galaxy, which are user-specified.
    """
    mins_rate = randint(TASA_MINS.min, TASA_MINS.max)
    deut_rate = randint(TASA_MINS.min, TASA_MINS.max)
    now = datetime.now().replace(microsecond=0)

    return {"nombre": nombre,
            "raza": raza,
            "galaxia": galaxia,
            "ultima_recoleccion": now,
            "magos": 0,
            "soldados": 0,  # There's an ordering here which is NOT guaranteed!
            "conquistado": False,
            "nivel_ataque": 0,
            "nivel_economia": 0,
            "torre": False,
            "cuartel": False,
            "tasa_minerales": mins_rate,
            "tasa_deuterio": deut_rate}


class Edificio():
    def __init__(self, vida):
        "docstring"
        self.vida = vida
        self.built = False

        
class Cuartel(Edificio):
    def __init__(self,):
        "docstring"
        super().__init__(vida=VIDA_CUARTEL)
        

class Torre(Edificio):
    def __init__(self):
        "docstring"
        super().__init__(vida=VIDA_TORRE)

    @property
    def ataque(self):
        if self.built:
            return ATAQUE_TORRE
        else:
            return 0


class Planet(object):
    """Documentation for Planeta

    """
    # TODO: Clean this up
    def __init__(self, nombre="UNSET", raza="Asesino",
                 galaxia="UNSET", **kwargs):
        super(Planet, self).__init__()

        # This avoids a weird recursion with properties
        self._soldados = 0
        self._magos = 0
        
        if not kwargs:
            attrs = _planet_defaults(nombre, raza, galaxia)
        else:
            attrs = {"nombre": nombre, "raza": raza, "galaxia": galaxia}
            attrs.update(kwargs)
        for key, value in attrs.items():
            setattr(self, key, value)

    def __str__(self):
        temp = red("{0:^20}") +\
               green("\t{1:30}")
        return "\n".join([temp.format(str(attr).strip("_").title(), str(val))
                          for attr, val in self.__dict__.items()])

    def __repr__(self):
        s = "Planet(\"%s\" Raza:(%s) Evo:[%f])" %\
            (self.nombre, self.raza.name, self.evolucion)
        return s

    @property
    def torre(self):
        return self._torre

    @torre.setter
    def torre(self, bool_):
        self._torre = Torre()
        self._torre.built = bool_
    
    @property
    def raza(self):
        try:
            return self._raza
        except AttributeError:
            raise Exception("Planet has not been properly initialized!"
                            "Check for the order of kwargs")

    @raza.setter
    def raza(self, raza_str):
        self._raza = {"Maestro": MaestroRaza,
                      "Aprendiz": AprendizRaza,
                      "Asesino": AsesinoRaza}[raza_str]

    # Soldiers
        
    @property
    def max_soldados(self):
        return self.raza.max_pop - self.magos
        
    @property
    def soldados(self):
        return self._soldados

    @soldados.setter
    def soldados(self, value):
        self._soldados = min(max(value, 0), self.max_soldados)

    # Mages
        
    @property
    def max_magos(self):
        if not self.raza.has_mago:
            return 0
        else:
            return self.raza.max_pop - self.soldados
        
    @property
    def magos(self):
        return self._magos

    @magos.setter
    def magos(self, value):
        self._magos = max(min(value, self.max_magos), 0)

    # Economy

    @property
    def tasa_minerales(self):
        return self._tasa_minerales

    @tasa_minerales.setter
    def tasa_minerales(self, valor):
        self._tasa_minerales = min(max(valor, TASA_MINS.min), TASA_MINS.max)

    @property
    def effective_tasa_minerales(self):
        lvl = self.nivel_economia
        multiplier = {0: 1, 1: 1.2, 2: 1.5, 3: 2}  # Level: Multiplier
        return self._tasa_minerales * multiplier[lvl]

    @property
    def tasa_deuterio(self):
        return self._tasa_deuterio

    @tasa_deuterio.setter
    def tasa_deuterio(self, valor):
        self._tasa_deuterio = min(max(valor, TASA_DEUT.min), TASA_DEUT.max)

    @property
    def effective_tasa_deuterio(self):
        lvl = self.nivel_economia
        multiplier = {0: 1, 1: 1.2, 2: 1.5, 3: 2}  # Level: Multiplier
        return self._tasa_deuterio * multiplier[lvl]

    @property
    def evolucion(self):
        return self.nivel_economia + self.nivel_ataque\
            + (self.soldados + self.magos)/(self.raza.max_pop)\
            + int(self.torre) + int(self.cuartel)


class Galaxy(object):
    """Documentation for Galaxy

    """
    def __init__(self, **kwargs):
        super(Galaxy, self).__init__()
        self.planets = {}

        if not kwargs:
            attrs = {"nombre": "UNSET",
                     "minerales": 1000,
                     "deuterio": 1000}
        else:
            attrs = kwargs
        for key, val in attrs.items():
            setattr(self, key, val)

    @property
    def planets_list(self):
        return list(self.planets.values())

    @property
    def minerales(self):
        return self._minerales

    @minerales.setter
    def minerales(self, value):
        self._minerales = int(value)

    @property
    def deuterio(self):
        return self._deuterio

    @deuterio.setter
    def deuterio(self, value):
        self._deuterio = int(value)

    def __repr__(self):
        s = "%s (%i planets)" % (self.nombre, len(self.planets))
        return s

    def __str__(self):
        return self.nombre


class Universe(object):
    """Main data-holding object with galaxies and planets"""

    def __init__(self):
        self.galaxies = {}
        self._acquire_planets_and_galaxies()

    def __repr__(self):
        s = "Universe with %i galaxies:\n" % len(self.galaxies)
        s += "\t" + "\n\t".join([str(g) for g in self.galaxies])
        return s

    @property
    def galaxies_list(self):
        return list(self.galaxies.values())

    def _acquire_planets_and_galaxies(self):
        """
        Initialize planet and galaxy objects based on the written data

        pop is used in the constructors to ensure said attributes are
        initialized before others (as they are used in some setters)

        Planets and Galaxies are loaded in as dicts to ease their
        assignment to each other before being turned into lists.
        """
        planets = {p["nombre"]: Planet(raza=p.pop("raza"),
                                       magos=p.pop("magos"),
                                       **p)
                   for p in read_planets()}

        self.galaxies = {g["nombre"]: Galaxy(**g)
                         for g in read_galaxies()}

        # Set the galaxies' planets and the planets' galaxies
        for p in planets.values():
            galaxy_name = p.galaxia

            # Give planet a parent galaxy as an object
            p.galaxia = self.galaxies[galaxy_name]

            # Give galaxy its child planet
            self.galaxies[galaxy_name].planets[p.nombre] = p

    def write_content(self):
        galaxies = [deepcopy(g.__dict__) for g in self.galaxies_list]

        planets = [deepcopy(p.__dict__) for g in self.galaxies_list
                   for p in g.planets_list]

        # A HACK to get the race names from the uninstantiated race classes
        # And to fix galaxy name
        for p in planets:
            p['_raza'] = str(p['_raza']).split(".")[-1][:-6]  # Awfuuuuuul
            p['galaxia'] = p['galaxia'].nombre

        # Remove planets list in galaxy entry
        for g in galaxies:
            g.pop("planets")

        write_csv(planets, "archivos\\planetas.csv")
        write_csv(galaxies, "archivos\\galaxias.csv")


if __name__ == '__main__':
    u = Universe()
