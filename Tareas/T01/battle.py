"""
Battle_Turns: generator that yields combatants at the end of every turn


"""

from collections import namedtuple
from random import randrange, shuffle

soldier = namedtuple("soldado", "ataque vida")
mage = namedtuple("mago", "ataque vida")


class Entity:
    """
    Adapter for planets and archmage for battle systems

    This must be initialized as soon as the Play Galaxy Menu is selected,
    as the lives and attack of soldiers and mage increase after a successful
    battle, data which, however, is not saved into the csv files. This means
    that life and attack are consistent for a unique playing session in which a
    player would need to invade multiple planets to witness this increase.

    Thus, these increases are lost upon reentering the game from the main menu.
    """
    def __init__(self, planet):
        "docstring"
        self.planet = planet
        self.name = planet.nombre

        self.race = planet.raza
        self.habilidad = self.race.habilidad
        
        self.cuartel = planet.cuartel
        self.torre = planet.torre
        self.soldados, self.magos = None, None

        self.is_player = False
        self.being_invaded = False

        self.generate_units()

    def generate_units(self):
        """Generate soldiers and mages with individual lives and attacks"""
        self.soldados = [soldier(randrange(*self.race.rango_atq_soldado),
                                 randrange(*self.race.rango_vid_soldado))
                         for i in range(self.planet.soldados)]

        self.magos = [mage(randrange(*self.race.rango_atq_mago),
                           randrange(*self.race.rango_vid_mago))
                      for i in range(self.planet.magos)]

        self._initial_life_set = False

    @property
    def ataque(self):
        if self.soldados:
            atk = sum(map(lambda x: x.ataque, self.soldados))
        if self.magos:
            atk += sum(map(lambda x: x.ataque, self.magos))
        atk += self.torre.ataque
        return atk

    @property
    def vida(self):
        # Once initial life has been set, it can be decreased through attacks
        if self._initial_life_set:
            return self._vida

        # Otherwise, initial life is sum of all combatants' lives
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
        pass

    def steal_minerals(self, enemy):
        pass

    def calculate_survivors(self):
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
            survivors = min(self.initial_life / mage_life, len(self.magos))
            self.planet.magos = survivors

            # Kill off the dead and improve the survivors
            shuffle(self.magos)
            [self.magos.pop() for i in range(len(self.magos) - survivors)]
            for m in self.magos:
                m = mage(m.ataque + 5, m.vida + 10)

        if self.soldados:

            # Calculate survivors
            soldier_life = sum(self.race.rango_vid_soldado) // 2
            survivors = self.initial_life - self.planet.magos*mage_life
            survivors //= soldier_life
            self.planet.soldados = survivors

            # Kill off the dead and improve the survivors
            shuffle(self.soldados)
            [self.soldados.pop() for i in range(len(self.soldados) - survivors)]
            for s in self.soldados:
                s = soldier(s.ataque + 5, s.vida + 10)


class Battle:
    def __init__(self, attacker, defender):
        "docstring"
        self.attacker, self.defender = attacker, defender

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

    def _execute_attack(self):
        attack = self.attacker.ataque
        defense = self.defender.vida

        self.defender.vida -= attack - defense

    def _generate_info(self, attack, defense, life_or, life_final):
        s = "Turno {turn_n} de la batalla entre {atkr} y {defr}\n\n"
        if self.attacker_ability:
            s += "Agresor {atkr} ha usado su habilidad!\n\t"
            s += self.attacker_ability + "\n"
        if self.defender_ability:
            s += "Defendiente {defr} ha usado su habilidad!\n\t"
            s += self.defender_ability + "\n"
        s += "{atkr} ataca a {defr} con {attk} puntos de ataque!\n"\
             "{defr} se defiende con {defs} puntos de defensa.\n\n"\
             "El ataque efectivo es {effc} puntos. Los {life_or} puntos"\
             "de vida de {defr} se reducen a {final_life}!\n\n"

        s += "{atkr} permanece con {life_atkr} puntos de vida"
        return s.format(turn_n=self.turn,
                        atkr=self.attacker.name,
                        defr=self.defender.name,
                        attk=attack,
                        defs=defense,
                        effc=attack - defense,
                        life_or=life_or,
                        final_life=life_final,
                        life_atkr=self.attacker.vida)
    
    def battle_turns(self):
        self.turn = 1
        while self.defender.vida > 0:

            self._activate_abilities()
            attack = self.attacker.ataque
            defense = self.defender.ataque
            
            or_life = self.defender.vida
            final_life = or_life - attack + defense

            self.defender.vida = final_life

            info = self._generate_info(attack, defense, or_life, final_life)
            yield info

            self._swap_attacker_defender()
            self.turn += 1

        self.defender.calculate_survivors()


if __name__ == '__main__':
    from universe import Planet, Galaxy
    g = Galaxy()
    g.nombre = "Galaxia"
    p1 = Planet(nombre="Planet1", raza="Maestro", galaxia=g)
    p2 = Planet(nombre="Planet2", raza="Aprendiz", galaxia=g)

    p1.soldados = 50
    p2.soldados = 30
    
    e1 = Entity(p1)
    e2 = Entity(p2)

    for turn in Battle(e1, e2).battle_turns():
        print(turn)
