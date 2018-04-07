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

    def steal_minerals(self, enemy, amount):
        if self.is_player:
            self.planet.galaxia.minerales += amount
        else:
            # They can't steal more minerals than we have!
            stolen_amount = min(amount, enemy.planet.galaxia.minerales)
            enemy.planet.galaxia.minerales -= stolen_amount

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

        # For printing turns
        self._initial_order = [attacker, defender]

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
        s = "Turno {turn_n} de la batalla entre {first} y {scnd}\n"
        s += "Vida:\n\t{first}: {life_1}\t{scnd}: {life_2}\n"
        if self.attacker_ability:
            s += "Agresor {atkr} ha usado su habilidad!\n\t"
            s += self.attacker_ability + "\n"
        if self.defender_ability:
            s += "Defendiente {defr} ha usado su habilidad!\n\t"
            s += self.defender_ability + "\n"
        s += "{atkr} ataca a {defr} con {attk} puntos de ataque!\n"\
             "Los {life_or} puntos de vida de {defr} se "\
             " reducen a {final_life}!\n\n"
        return s.format(turn_n=self.turn,
                        first=self._initial_order[0].name,
                        scnd=self._initial_order[1].name,
                        life_1=self._initial_order[0].vida,
                        life_2=self._initial_order[1].vida,
                        atkr=self.attacker.name,
                        defr=self.defender.name,
                        attk=attack,
                        life_or=life_or,
                        final_life=final_life)
    
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

        if self.attacker.is_player:
            input(self.attacker.race.warcry)
        self.defender.calculate_survivors()


if __name__ == '__main__':
    from universe import Planet, Galaxy
    g = Galaxy()
    g.nombre = "Galaxia"
    p1 = Planet(nombre="Planet1", raza="Maestro", galaxia=g)
    p2 = Planet(nombre="Planet2", raza="Aprendiz", galaxia=g)

    minerals = []
    minerals.append(p1.galaxia.minerales)

    p1.soldados = 50
    p2.soldados = 30
    
    e1 = Entity(p1)
    e1.is_player = True
    e2 = Entity(p2)

    for turn in Battle(e1, e2).battle_turns():
        print(turn)

    minerals.append(p1.galaxia.minerales)

    assert(minerals[0] != minerals[1])
