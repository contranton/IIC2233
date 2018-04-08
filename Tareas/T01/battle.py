"""
Battle_Turns: generator that yields combatants at the end of every turn


"""

from collections import namedtuple
from random import randrange, shuffle

from razas import aprendiz, asesino

soldier = namedtuple("soldado", "ataque vida")
mage = namedtuple("mago", "ataque vida")

ARCHMAGE_LIFE = 10000
ARCHMAGE_ATTACK = 400

class Entity:
    """
    Adapter for planets, player and archmage for battle systems

    This must be initialized as soon as the Play Galaxy Menu is selected,
    as the lives and attack of soldiers and mage increase after a successful
    battle, data which, however, is not saved into the csv files. This means
    that life and attack are consistent for a unique playing session in which a
    player would need to invade multiple planets to witness this increase.

    Thus, these increases are lost upon reentering the game from the main menu.
    """
    def __init__(self, galaxia, name, race, soldados, magos, cuartel, torre):
        "docstring"
        self.galaxia = galaxia
        self.name = name

        self.race = race

        self.cuartel = cuartel
        self.torre = torre

        self.soldados, self.magos = None, None

        self.is_player = False
        self.being_invaded = False

        self.dup_attack = False

    def habilidad(self, attacker, defender):
        # Must be overwritten for Archimago
        return self.race.habilidad(attacker, defender)

    def generate_units(self, num_soldados, num_magos):
        """Generate soldiers and mages with individual lives and attacks"""
        self.soldados = [soldier(randrange(*self.race.rango_atq_soldado),
                                 randrange(*self.race.rango_vid_soldado))
                         for i in range(num_soldados)]

        self.magos = [mage(randrange(*self.race.rango_atq_mago),
                           randrange(*self.race.rango_vid_mago))
                      for i in range(num_magos)]

        self._initial_life_set = False

    @property
    def ataque(self):
        if self.soldados:
            atk = sum(map(lambda x: x.ataque, self.soldados))
        if self.magos:
            atk += sum(map(lambda x: x.ataque, self.magos))
        if self.being_invaded:
            atk += self.torre.ataque
        if self.dup_attack:
            atk *= 2
            self.dup_attack = False

        return atk

    @property
    def vida(self):
        # Once initial life has been set, it can be decreased through attacks
        if self._initial_life_set:
            return self._vida

        # Otherwise, initial life is sum of all combatants' lives
        life = 0
        if self.soldados:
            life = sum(map(lambda x: x.vida, self.soldados))
        if self.magos:
            life += sum(map(lambda x: x.vida, self.magos))
        self._vida = life
        self.initial_life = life
        self._initial_life_set = True

        return life

    @vida.setter
    def vida(self, value):
        self._vida = value

    def duplicate_attack(self):
        self.dup_attack = True

    def steal_minerals(self, amount):
        if self.is_player:
            self.galaxia.minerales += amount
        else:
            # They can't steal more minerals than we have!
            stolen_amount = min(amount, self.galaxia.minerales)
            self.galaxia.minerales -= stolen_amount

    def calculate_survivors(self, planet=None):
        """
        Calculates surviving combatants after a battle and updates this
        entity's soldiers and mages lists by removing random KIAs and
        improving the stats of the survivors

        For simplicity, we take the "average life" to be the mean of the
        possible life range for both soldiers and mages.

        Upon finishing a battle, the surviving units increase their life and
        attack by 10 and 5 points, respectively. We'll assume that, since
        this in a way means that they're getting stronger, the min and max
        values used for attack and life generation don't limit this value.
        """
        mage_life = 0
        if self.magos:

            # Calculate survivors
            mage_life = sum(self.race.rango_vid_mago) // 2
            survivors = min(self.vida / mage_life, len(self.magos))
            if planet:
                planet.magos = survivors

            # Kill off the dead and improve the survivors
            shuffle(self.magos)
            [self.magos.pop() for i in range(len(self.magos) - survivors)]
            for m in self.magos:
                m = mage(m.ataque + 5, m.vida + 10)

        if self.soldados:

            # Calculate survivors
            soldier_life = sum(self.race.rango_vid_soldado) // 2
            survivors = self.vida - len(self.magos)*mage_life
            survivors //= soldier_life
            if planet:
                planet.soldados = survivors

            # Kill off the dead and improve the survivors
            shuffle(self.soldados)
            [self.soldados.pop() for i in range(len(self.soldados) - survivors)]
            for s in self.soldados:
                s = soldier(s.ataque + 5, s.vida + 10)


class Archimago(Entity):

    def __init__(self, galaxia):
        "docstring"
        super().__init__(galaxia=galaxia,
                         name="El Archi-Mago",
                         race="Archimago",
                         soldados=0,
                         magos=0,
                         cuartel=False,
                         torre=False)
        self.vida = ARCHMAGE_LIFE
        self._initial_life_set = True

    def habilidad(self, attacker, defender):
        s = asesino.habilidad(attacker, defender)
        s += aprendiz.habilidad(attacker, defender)
        return s

    @Entity.vida.getter
    def vida(self):
        return self._vida

    @vida.setter
    def vida(self, value):
        self._vida = value

    @Entity.ataque.getter
    def ataque(self):
        return ARCHMAGE_ATTACK


class Battle:
    def __init__(self, galaxy, attacker, defender):
        "Defender is always a planet!"
        self.make_entities(galaxy, attacker, defender)

        self.attacker_ability = None
        self.defender_ability = None

        self.turn = 0

    def _swap_attacker_defender(self):
        self.attacker, self.defender = self.defender, self.attacker

    def _activate_abilities(self):
        """TODO: Clean me up pls"""
        self.attacker_ability = self.attacker.habilidad(self.attacker,
                                                        self.defender)
        self.defender_ability = self.defender.habilidad(self.defender,
                                                        self.attacker)

    def _generate_info(self, attack, life_or, final_life):
        s = "Turno {turn_n} de la batalla entre {atkr.name} y {defr.name}\n"
        s += ("Vida:\n\t{atkr.name}: {atkr.vida}\t" +
              "{defr.name}: {defr.vida}\n\n")
        if self.attacker_ability:
            s += "Agresor {atkr.name} ha usado su habilidad!\n\t"
            s += self.attacker_ability + "\n"
        if self.defender_ability:
            s += "Defendiente {defr.name} ha usado su habilidad!\n\t"
            s += self.defender_ability + "\n"
        s += "{atkr.name} ataca a {defr.name} con {attk} puntos de ataque!\n"\
             "Los {life_or} puntos de vida de {defr.name} se "\
             " reducen a {final_life}!\n\n"
        return s.format(turn_n=self.turn,
                        atkr=self.attacker,
                        defr=self.defender,
                        attk=attack,
                        life_or=life_or,
                        final_life=final_life)

    def make_entities(self, galaxy, attacker, defending_planet):
        if isinstance(attacker, Archimago):
            self.attacker = attacker
        else:
            self.attacker = Entity(galaxy,
                                   name=attacker.nombre,
                                   race=attacker.raza,
                                   soldados=attacker.soldados,
                                   magos=attacker.magos,
                                   cuartel=attacker.cuartel,
                                   torre=attacker.torre)
            self.attacker.generate_units(attacker.soldados,
                                         attacker.magos)

        self.defender = Entity(galaxy,
                               name=defending_planet.nombre,
                               race=defending_planet.raza,
                               soldados=defending_planet.soldados,
                               magos=defending_planet.magos,
                               cuartel=defending_planet.cuartel,
                               torre=defending_planet.torre)
        
        self.defender.generate_units(defending_planet.soldados,
                                     defending_planet.magos)
        self.defending_planet = defending_planet

    def battle_turns(self):
        self.turn = 1
        while self.defender.vida > 0:
            self._swap_attacker_defender()

            self._activate_abilities()
            attack = self.attacker.ataque

            or_life = self.defender.vida
            final_life = max(or_life - attack, 0)

            info = self._generate_info(attack, or_life, final_life)
            self.defender.vida = final_life
            yield info

            self.turn += 1

        if self.defender.being_invaded:
            self.defending_planet.soldados = 0
            self.defending_planet.magos = 0

        self.attacker.calculate_survivors()

        if isinstance(self.attacker, Archimago):
            self.defending_planet.maximize_stats()
            self.defending_planet.conquistado = False
        elif self.attacker.is_player:
            input(self.attacker.race.warcry)
            self.defending_planet.conquistado = True

    def update_attacker(self, planet_attacker):
        i = self.defender
        if self.attacker.being_invaded:
            i = self.attacker
            
        planet_attacker.soldados = len(i.soldados)
        planet_attacker.magos = len(i.magos)


if __name__ == '__main__':
    from universe import Planet, Galaxy
    from colorama.ansi import clear_screen as CLS
    g = Galaxy()
    g.nombre = "Galaxia"
    p1 = Planet(nombre="Planet1", raza="Maestro", galaxia=g)
    p2 = Planet(nombre="Planet2", raza="Aprendiz", galaxia=g)

    minerals = []
    minerals.append(p1.galaxia.minerales)

    p1.soldados = 50
    p2.soldados = 30

    for turn in Battle(g, p1, p2).battle_turns(p2):
        print(CLS()+turn)

    minerals.append(p1.galaxia.minerales)

    assert(minerals[0] != minerals[1])

    a = Archimago(g)

    p1.galaxia.minerales += 2000
    minerals.append(p1.galaxia.minerales)

    for turn in Battle(g, a, p1).battle_turns(p1):
        print(CLS()+turn)

    assert(minerals[2] != p1.galaxia.minerales)
