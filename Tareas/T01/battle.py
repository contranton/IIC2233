"""
Battle_Turns: generator that yields combatants at the end of every turn


"""


class Combatant:
    def __init__(self, planet):
        "docstring"
        self.race = planet.raza
        self.cuartel = cuartel.torre
        self.torre = planet.torre

def battle_turns(c1, c2):
    attacker, defender = c1, c2

    while attacker.vida > 0 and defender.vida > 0:
        calculate_attacks()
        activate_abilities()
        update_life()

        yield "Something"

        attacker, defender = defender, attacker

    calc_survivors()
