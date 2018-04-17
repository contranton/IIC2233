from random import shuffle

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

        self.t1_goals = self.team1.calculate_goals()
        self.t2_goals = self.team2.calculate_goals()

        self.t1_cards = self.team1.calculate_cards()
        self.t2_cards = self.team2.calculate_cards()

        if self.t1_goals == self.t2_goals:
            print("EMPATE")
            
        elif self.t1_goals > self.t2_goals:
            print("TEAM 1 WINS")
            self.winner = self.team1
            self.loser = self.team2
        else:
            print("TEAM 2 WINS")
            self.winner = self.team2
            self.loser = self.team1
 

class xTournament(object):
    """
    Inverted tree structure
    16-team tournament implies 4 total levels

    Losers in semi-finals must play a round to set third-place
    """
    def __init__(self, equipos):
        self.teams = xList()
        for team_name, team_hope in xList(*equipos):
            self.teams.append(xTeam(team_name, team_hope))

        self.bracket = xDict()
        self.bracket[0] = self.make_bracket()

        self.current_level = 0

    def make_bracket(self):
        bkt = xDict()
        shuffle(self.teams)

        i = 0
        while i < len(self.teams)//2:
            bkt[i] = xGame(i, self.teams[2*i], self.teams[2*i+1])
            i += 1
        return bkt

    def play_round(self):
        level = self.current_level
        for game in self.bracket[level]:
            game.play()


if __name__ == '__main__':
    pass
