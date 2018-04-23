from sys import stdout
from random import randrange

from structs.xDict import xDict
from structs.xList import xList
from structs.xGraph import xGraph


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

        # Convoluted thing used to remove them from user team
        # if they were added randomly due to the team not being
        # completely full
        self.transitory = False

    def __repr__(self):
        s = "xPlayer({}, {})"
        s = s.format(self.alias, self.overall)
        return s

    def __eq__(self, other):
        return id(self) == id(other)

    def __id__(self):
        return self.ID


class xTeam():
    def __init__(self, name, players=None):
        self.name = name

        self.players = xList(*players) if players else xList()
        self.game_hope = None

        # So that we avoid recalculating affinities
        # for the same team
        self.all_calculated = False

        # Only set for non-user teams in 'simple'
        # tournament mode
        self._initial_hope = None

    def __repr__(self):
        s = "Equipo({})"
        return s.format(self.name)

    def __str__(self):
        return self.name

    @property
    def quality(self):
        return sum(xList(*map(lambda x: x.overall, self.players))) / 11

    @property
    def initial_hope(self):
        if self._initial_hope:
            return self._initial_hope
        return self.calculate_total_affinity() * self.quality

    @initial_hope.setter
    def initial_hope(self, val_):
        self._initial_hope = val_

    def delete_player(self, player):
        i = 0
        for p in self.players:
            if p == player:
                self.players.remove(i)
                return
            i += 1

    def add_player(self, player: xPlayer):
        if len(self.players) < 11:
            self.players.append(player)
        else:
            raise ValueError("TOO MANY PLAYERS BRUH")

    def fill_random_players(self, player_list: xList, transitory=False):
        # CAn't use random.sample cus we can't let xList
        # inherit from Sequence -__-
        i = len(self.players)
        while i < 11:
            x = randrange(len(player_list))
            player = player_list[x]
            if player.assigned:
                continue

            player.transitory = transitory
            self.add_player(player)
            i += 1

    def calculate_player_affinities(self, player_graph):
        if self.all_calculated:
            return
        print("Calculando afinidades entre jugadores del equipo %s" %
              self.name)
        for player in self.players:
            print(".", end="", flush=True)
            affs = player_graph.get_player_affinities(player, self)
            for other, aff in affs:
                player.affinity[other.ID] = 1 - aff
                other.affinity[player.ID] = 1 - aff
        if len(self.players) == 11:
            self.all_calculated = True
        print("\tListo")

    def calculate_total_affinity(self) -> float:
        aff = 0
        for player in self.players:
            for other in self.players:
                try:
                    aff += player.affinity[other.ID]
                except KeyError:
                    # Player has no affinity with himself
                    continue
        return aff / (11*11)

    def calculate_faults(self):  # -> xList[xPlayer]
        faults = xList()

        # If simple mode
        if self._initial_hope:
            num = min(int(self._initial_hope//60 + randrange(2)), 11)
            for i in range(num):
                faults.append(self.players[i])
            return faults

        # If real mode
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


class xPlayerGraph():
    def __init__(self, player_list):  # xList[xPlayer]
        print("Creando conexiones iniciales de jugadores")
        self.graph = xGraph(player_list)
        for node in self.graph.nodes:
            print(".", end="", flush=True)
            p1 = node.content
            for other in self.graph.nodes:
                p2 = other.content
                if p1 == p2:
                    continue

                # Natl & Club -> Close Friends
                if p1.natl == p2.natl and p1.club == p2.club:
                    node.add_sibling(other, 1)

                    # 1 Is the largest affinity so we can set it
                    # immediately
                    p1.affinity[p2.ID] = 1
                    p2.affinity[p1.ID] = 1

                # Natl & Club -> Far Friends
                elif p1.natl == p2.natl and p1.league == p2.league:
                    node.add_sibling(other, 0.95)

                # Natl | Club | League -> Acquaintances
                elif (p1.natl == p2.natl or p1.club == p2.club
                      or p1.league == p2.league):
                    node.add_sibling(other, 0.9)
        print("Conexiones iniciales terminadas")

    def get_player_affinities(self, player, team):
        destinations = xList(
            *filter(
                lambda x: x != player and x.ID not in player.affinity.keys(),
                team.players)
        )

        return self.graph.get_shortest_distance_multiple_dests(
            player, destinations, transform=lambda x: 1-x)

    # Hnggggg these are so pythonic <3<3<3

    def get_best_friend(self, player):
        return self.graph.get_closest(player, transform=lambda x: 1 - x).content

    def get_worst_friend(self, player):
        return self.graph.get_closest(player, transform=lambda x: x).content

    def get_most_popular(self):
        return max(self.graph.nodes, key=lambda n: len(n.siblings)).content

    def star_choice(self, player):
        chisp = xList()
        others = self.graph.get_nearest(player, threshold=1,
                                        transform=lambda x: 1 - x)
        for other in others:
            player = other.content
            # Other.total_distance es la afinidad
            aff = 1 - other.total_distance
            chisp.append(xList(player, aff * player.overall))

        return max(chisp, key=lambda c: c[1])[0]
