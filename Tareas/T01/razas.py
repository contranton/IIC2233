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
                 " nuevo planeta!\n")
            self.warcry = s + self.__class__.warcry
        else:
            del self
            raise Exception("Instantiated multiple race classes" +
                            ". We're a singleton bruh.")

    def __repr__(self):
        return self.name

    @staticmethod
    def habilidad(battle):
        """Special race ability, used in battles"""
        pass

    @property
    def warcry(self):
        s = self._warcry
        return s

    @warcry.setter
    def warcry(self, value):
        self._warcry = value


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
    def habilidad(battle):
        entity, enemy_entity = battle.attacker, battle.defender
        if not entity.being_invaded:
            return ""

        if not battle.turn == 1:
            return ""

        # 30% chance
        if randrange(10) in range(3):
            s = enemy_entity.soldados
            s = s[:(len(s)//2)]

            m = enemy_entity.magos
            m = m[:(len(s)//2)]

            s = entity.name + " ha destruido la mitad del ejercito de "
            s += enemy_entity.name + "!!"
            return s

        return ""


class AprendizRaza(Raza):

    name = "Aprendiz"

    max_pop = 100

    costo_soldado = Cost(mins=300, deut=400)
    rango_atq_soldado = (30, 60)
    rango_vid_soldado = (600, 700)

    warcry = ("¡Con una gran defensa y medicinas,nuestros"
              "soldados son invencibles!")

    @staticmethod
    def habilidad(battle):
        entity, enemy_entity = battle.attacker, battle.defender
        if entity.being_invaded:
            return ""

        # 70% chance
        if randrange(10) in range(7):
            entity.steal_minerals(200)
            s = entity.name + " le roba 200 minerales a "
            s += enemy_entity.name
            return s

        return ""


class AsesinoRaza(Raza):

    name = "Asesino"

    max_pop = 400

    costo_soldado = Cost(mins=100, deut=200)
    rango_atq_soldado = (40, 45)
    rango_vid_soldado = (250, 270)

    warcry = ("¡El poder de las sombras es lo único "
              "necesario para ganar estas batallas!")

    @staticmethod
    def habilidad(battle):
        entity, enemy_entity = battle.attacker, battle.defender
        if entity.being_invaded:
            return ""

        # 40% chance
        if randrange(10) in range(4):
            entity.duplicate_attack()
            return entity.name + " adquiere doble ataque!"

        return ""


maestro = MaestroRaza()
aprendiz = AprendizRaza()
asesino = AsesinoRaza()
