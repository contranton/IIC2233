from random import shuffle, randrange
from math import log2

from structs.xList import xList
from structs.xDict import xDict
from structs.xTeam import xTeam


class xGame(object):
    def __init__(self, id, team1, team2) -> None:
        self.id = id
        if len(team1.players) < 11 or len(team2.players) < 11:
            print(team1.players)
            print(team2.players)
            raise Exception("INSUFFICIENT PLAYERS FOR TEAMS")
        self.team1 = team1
        self.team2 = team2
        self.winner = None
        self.loser = None

        self.results = xDict()

        self.played = False

    def __repr__(self):
        return "<Juego {} entre {} y {}>".format(self.id,
                                                 self.team1.name,
                                                 self.team2.name)

    def __str__(self):
        s = "{}: {} vs. {}"
        return s.format(self.id, str(self.team1),
                        str(self.team2), str(self.winner))

    def play(self):
        if self.played:
            raise Exception("This round has already been played")
        self.played = True

        for team in xList(self.team1, self.team2):
            faults = team.calculate_faults()

            hope = team.calculate_game_hope(len(faults))
            goals = team.calculate_goals(hope)
            cards = team.calculate_cards()

            self.results[team.name] =\
                xDict(xList("hope", "goals", "cards", "faults"),
                      xList(hope, goals, cards, faults))
        self._pick_winner()

    def _pick_winner(self):
        r1, r2 = self.results[self.team1.name], self.results[self.team2.name]
        if r1["goals"] == r2["goals"]:
            # PENALTIES
            best = self.team1 if r1["hope"] > r2["hope"] else self.team2
            worst = self.team2 if best is self.team1 else self.team1
            if randrange(10) in range(8):
                self.winner = best
                self.loser = worst
            else:
                self.winner = worst
                self.loser = best

        elif r1["goals"] > r2["goals"]:
            self.winner = self.team1
            self.loser = self.team2
        else:
            self.winner = self.team2
            self.loser = self.team1
 

class xTournament(object):
    """
    Inverted tree structure
    16-team tournament implies 4 total levels

    Losers in semi-finals must play a round to set third-place
    """
    def __init__(self, equipos):  #: xList[xTeam]):
        self.teams = xDict()
        for eq in equipos:
            self.teams[eq.name] = eq

        self.bracket = xDict()
        self.bracket[0] = self.make_initial_bracket()

        self.current_level = 0

    @property
    def games(self):
        g = xList()
        for level in self.bracket.values():
            for game in level.values():
                g.append(game)
        return g

    def make_initial_bracket(self):
        bkt = xDict()

        teams = self.teams.values().copy()
        shuffle(teams)

        i = 0
        while i < len(teams)//2:
            bkt[i] = xGame(i, teams[2*i],
                           teams[2*i+1])
            i += 1
        return bkt

    def play_round(self):
        level = self.current_level
        bkt = self.bracket[level]

        # Pair up teams in pairs for each bracket
        paired_up = xList()
        j = 0
        while j < len(bkt)//2:
            paired_up.append(
                xList(bkt.values()[2*j], bkt.values()[2*j+1])
            )
            j += 1

        i = bkt.keys()[-1] + 1
        self.bracket[level+1] = xDict()
        for game1, game2 in paired_up:
            game1.play()
            game2.play()
            if level < log2(len(self.teams.values())):
                next_bkt = xGame(i, game1.winner, game2.winner)
                self.bracket[level+1][i] = next_bkt
                i += 1
        self.current_level += 1

    def simulate(self):
        while self.current_level < log2(len(self.bracket[0])):
            self.play_round()

        last_game = self.bracket[self.current_level].values()[0]
        last_game.play()
        self.last_game = last_game

        # Losers of second-to-last round play the 3rd place match
        p1 = self.bracket[self.current_level - 1].values()[0].loser
        p2 = self.bracket[self.current_level - 1].values()[1].loser
        self.third_round_game = xGame(last_game.id + 1, p1, p2)
        self.third_round_game.play()
        self.bracket[self.current_level] = self.third_round_game

        self.first = last_game.winner
        self.second = last_game.loser
        self.third = self.third_round_game.winner


if __name__ == '__main__':
    pass
