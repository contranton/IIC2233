from random import randrange

from structs.xDict import xDict
from structs.xList import xList


class xPlayer(object):
    def __init__(self, ID, alias, name, club, league, natl, overall):
        self.ID = int(ID)
        self.alias = alias
        self.name = name
        self.club = club
        self.league = league
        self.natl = natl
        self.overall = int(overall)

        # Affinity with other players
        self.affinity = xDict()

        self.assigned = False

    def __repr__(self):
        s = "xPlayer({}, {})"
        s = s.format(self.alias, self.overall)
        return s


class xTeam():
    """Documentation for xTeam, ONLY FOR PLAYER TEAM

    """
    def __init__(self, name, players=xList()):
        self.name = name

        self.players = xList(*players)
        self.game_hope = None

    def __repr__(self):
        s = "Equipo({})"
        return s.format(self.name)

    def __str__(self):
        return self.name

    @property
    def quality(self):
        return sum(map(lambda x: x.overall, self.players)) / 1089

    @property
    def initial_hope(self):
        return self.calculate_total_affinity() * self.quality

    def add_player(self, player: xPlayer):
        if len(self.players) < 11:
            self.players.append(player)
        else:
            raise Exception("TOO MANY PLAYERS BRUH")

    def fill_random_players(self, player_list: xList):
        # CAn't use random.sample cus we can't let xList
        # inherit from Sequence -__-
        i = 0
        while i < 11:
            x = randrange(len(player_list))
            player = player_list[x]
            if player.assigned:
                continue

            self.add_player(player)
            i += 1

    def calculate_player_affinities(self, player_graph=None):
        # TODO: implement for real
        for player in self.players:
            for other in self.players:
                if player != other:
                    player.affinity[other.ID] = 0.5

    def calculate_total_affinity(self) -> int:
        # TODO
        return 5

    def calculate_faults(self) -> xList(xPlayer):
        faults = xList()
        for player in self.players:
            prob = 5
            for other in self.players:
                try:
                    if player.affinity[other.name] < 0.8:
                        prob += 2
                except KeyError:
                    # Player has no affinity with himself
                    continue
            if randrange(100) in range(prob):
                faults.append(player)
        return faults

    def calculate_cards(self):  # -> xDict[str name, xDict[str type, int num]]
        cards = xDict()
        for player in self.players:
            cards[player.name] = xDict()
            if randrange(5) == 0:
                cards[player.name]["Amarilla"] = 1
            else:
                pass
                cards[player.name]["Amarilla"] = 0

            if randrange(20) == 0:
                cards[player.name]["Roja"] = 1
            else:
                pass
                cards[player.name]["Roja"] = 0
        return cards

    def calculate_game_hope(self, fault_num):
        return self.initial_hope * (1 - fault_num / 100)

    def calculate_goals(self, hope):
        return int((hope/40)**2)
