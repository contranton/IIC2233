class xPlayer(object):
    def __init__(self, ID, alias, name, club, league, natl, overall):
        super(xPlayer, self).__init__()
        self.ID = ID
        self.alias = alias
        self.name = name
        self.club = club
        self.league = league
        self.natl = natl
        self.overall = overall


class xTeam(object):
    def __init__(self, players):
        super(xTeam, self).__init__()
        self.players = players
