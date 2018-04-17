from random import shuffle, randrange
from math import log2

from structs.xList import xList
from structs.xDict import xDict
from structs.xTeam import xTeam


class xGame(object):
    def __init__(self, id, team1: xTeam, team2: xTeam) -> None:
        self.id = id
        self.team1 = team1
        self.team2 = team2
        self.winner = None
        self.loser = None

        self.played = False

    def __repr__(self):
        return "<Juego {} entre {} y {}>".format(self.id,
                                                 self.team1.name,
                                                 self.team2.name)
        
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
    def __init__(self, equipos: xList[xTeam]):
        self.teams = xList()
        for team_name, team_hope in xList(*equipos):
            # TODO: NEED TO GET PLAYERS IN HERE
            self.teams.append(xTeam(team_name, team_hope))

        self.bracket = xDict()
        self.bracket[0] = self.make_initial_bracket()

        self.current_level = 0

    def make_initial_bracket(self):
        bkt = xDict()
        shuffle(self.teams)

        i = 0
        while i < len(self.teams)//2:
            bkt[i] = xGame(i, self.teams[2*i], self.teams[2*i+1])
            i += 1
        return bkt

    def play_round(self):
        level = self.current_level
        # THIS IS UNINTENDED BEHAVIOR OF XLIST IMPLEMENTATION
        # Somehow, by doing zip(xList, xList) for equal xLists
        # returns two-tuples of contiguous elements O.o
        # Just what I was looking for though :D
        bkt = self.bracket[level]
        i = len(bkt)
        for game1, game2 in xList(*zip(bkt, bkt)):
            game1.play()
            game2.play()
            if level < log2(len(self.teams)):
                next_bkt = xGame(i, game1.winner, game2.winner)
                self.bracket[level+1][i] = next_bkt


if __name__ == '__main__':
    pass
