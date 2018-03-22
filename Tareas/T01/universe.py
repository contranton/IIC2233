from datetime import datetime
from random import randint

from razas import MaestroRaza, AprendizRaza, AsesinoRaza
from fileio import read_planets, read_galaxies

"""
Defines Planet, Galaxy, and Universe classes
"""


def _planet_defaults():
    """
    Returns the default values for a planet other than
    its name, race, and parent galaxy, which are user-specified.
    """
    mins_rate = randint(1, 10)
    deut_rate = randint(5, 15)
    now = datetime.now()
    
    return {"nombre": "UNSET",
            "raza": "Asesino",  # Only for defaulting -- is changed anyways
            "galaxia": "UNSET",
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


class Planet(object):
    """Documentation for Planeta

    """
    def __init__(self, **kwargs):
        super(Planet, self).__init__()
        if not kwargs:
            attrs = _planet_defaults()
        else:
            attrs = kwargs
        for key, value in attrs.items():
            setattr(self, key, value)

    def __repr__(self):
        s = "Planet(\"%s\" Raza:(%s) Evo:[%f])" %\
            (self.nombre, self.raza.name, self.evolucion)
        return s

    @property
    def raza(self):
        return self._raza

    @raza.setter
    def raza(self, raza_str):
        self._raza = {"Maestro": MaestroRaza,
                      "Aprendiz": AprendizRaza,
                      "Asesino": AsesinoRaza}[raza_str]

    @property
    def soldados(self):
        return self._soldados

    @soldados.setter
    def soldados(self, value):
        max_soldados = self.raza.max_pop - self.magos
        self._soldados = min(max(value, 0), max_soldados)

    @property
    def tasa_minerales(self):
        lvl = self.nivel_economia
        multiplier = {0: 1, 1: 1.2, 2: 1.5, 3: 2}  # Level: Multiplier
        return self._tasa_minerales * multiplier[lvl]

    @tasa_minerales.setter
    def tasa_minerales(self, valor):
        self._tasa_minerales = valor

    @property
    def tasa_deuterio(self):
        lvl = self.nivel_economia
        multiplier = {0: 1, 1: 1.2, 2: 1.5, 3: 2}  # Level: Multiplier
        return self._tasa_deuterio * multiplier[lvl]

    @tasa_deuterio.setter
    def tasa_deuterio(self, valor):
        self._tasa_deuterio = valor

    @property
    def evolucion(self):
        return self.nivel_economia + self.nivel_ataque\
            + (self.soldados + self.magos)/(self.raza.max_pop)\
            + int(self.torre) + int(self.cuartel)


class Galaxy(object):
    """Documentation for Galaxia

    """
    def __init__(self, **kwargs):
        super(Galaxy, self).__init__()
        if not kwargs:
            attrs = {"nombre": "UNSET"}
        else:
            attrs = kwargs
        for key, val in attrs.items():
            setattr(self, key, val)

        self.planets = []

    def __repr__(self):
        s = "%s (%i planets)" % (self.nombre, len(self.planets))
        return s


class Universe(object):
    """Main data-holding object with galaxies and planets"""

    def __init__(self):
        self.changes = None
        self._acquire_planets_and_galaxies()
        
    def __repr__(self):
        s = "Universe with %i galaxies:\n" % len(self.galaxies)
        s += "\t" + "\n\t".join([str(g) for g in self.galaxies])
        return s
    
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
            self.galaxies[galaxy_name].planets.append(p)

        # Make galaxies a list for easier access
        self.galaxies = list(self.galaxies.values())


if __name__ == '__main__':
    u = Universe()
