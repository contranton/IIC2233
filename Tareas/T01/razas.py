from abc import ABCMeta, abstractmethod
from collections import namedtuple
from random import randrange

"""
Since a race encodes the properties of the actions of multiple planets, it
makes no sense to instatiate them. Thus, they remain abstract classes!
"""

RACE_INSTANCES = set()
Cost = namedtuple("Cost", "mins deut")

class Raza(metaclass=ABCMeta):
    """Defines a race's properties, to be used in individual planets

    It behaves as a sort of configuration object, aggregated as
    necessary to planets that use it. Never instantiated!

    """

    name = ""

    has_mago = False

    warcry = "Test"

    def __init__(self):
        "docstring"
        if type(self) not in RACE_INSTANCES:
            RACE_INSTANCES.add(type(self))

            s = ("Wubba Lubba Dub Dub, hemos logrado conquistar un" +
                 " nuevo planeta\n")
            self.warcry = s + self.__class__.warcry
        else:
            del self
            raise Exception("Instantiated multiple race classes" +
                            ". We're a singleton bruh.")

    @staticmethod
<<<<<<< Updated upstream
    @abstractmethod
    def habilidad(entity, enemy_entity):
        """Special race ability, used in battles"""
        pass

<<<<<<< variant A
>>>>>>> variant B
    def habilidad(entity, enemy_entity):
        """Special race ability, used in battles"""
        pass

    @property
    def warcry(self):
        
        s += self._warcry
        return s

    @warcry.setter
    def warcry(self, value):
        self._warcry = value

======= end
=======
    @property
    @classmethod
    def warcry(cls):
        s = "Wubba Lubba Dub Dub, hemos logrado conquistar un nuevo planeta"
        s += cls._warcry
        return s

    @warcry.setter
    @classmethod
    def warcry(cls, value):
        cls._warcry = value

>>>>>>> Initial implementation of battle system

class MaestroRaza(Raza):

    name = "Maestro"

    max_pop = 100

    costo_soldado = Cost(mins=200, deut=300)
    rango_atq_soldado = (60, 80)
    rango_vid_soldado = (200, 250)

    has_mago = True
    costo_mago = Cost(mins=300, deut=400)
    rango_atq_mago = (80, 120)
    rango_vid_mago = (150, 200)

    warcry = ("¡Nuestro conocimiento nos ha "
              "otorgado una victoria más!")

    @staticmethod
    @abstractmethod
<<<<<<< HEAD
    def habilidad():
        pass
>>>>>>> Stashed changes
=======
    def habilidad(entity, enemy_entity):
        if not entity.being_invaded:
            return

        if not entity.turn_number == 0:
            return

        # 30% chance
        if randrange(10) in range(3):
            s = enemy_entity.soldados
            s = s[:(len(s)//2)]

            m = enemy_entity.magos
            m = m[:(len(s)//2)]

            return "Habilidad Maestro ha sido activada"
>>>>>>> Initial implementation of battle system


class AprendizRaza(Raza):

    name = "Aprendiz"
    
    max_pop = 100

    costo_soldado = Cost(mins=300, deut=400)
    rango_atq_soldado = (30, 60)
    rango_vid_soldado = (600, 700)

    warcry = "¡Con una gran defensa y medicinas,\nnuestros\
              soldados son invencibles!"

    @staticmethod
    @abstractmethod
    def habilidad(entity, enemy_entity):
        if entity.being_invaded:
            return

        # 70% chance
        if randrange(10) in range(7):
            entity.steal_minerals(enemy_entity)
            return "Aprendiz habilidad ha sido activada"


class AsesinoRaza(Raza):

    name = "Asesino"
    
    max_pop = 400

    costo_soldado = Raza.Cost(mins=100, deut=200)
    rango_atq_soldado = (40, 45)
    rango_vid_soldado = (250, 270)

    warcry = "¡El poder de las sombras es lo\núnico\
              necesario para ganar estas batallas!"

    @staticmethod
    @abstractmethod
    def habilidad(entity):
        if entity.being_invaded:
            return

        # 40% chance
        if randrange(10) in range(4):
            entity.duplicate_attack()
            return "Aprendiz habilidad ha sido activada"

maestro = MaestroRaza()
aprendiz = AprendizRaza()
asesino = AsesinoRaza()
