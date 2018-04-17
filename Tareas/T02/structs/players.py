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
    """Documentation for xTeam

    """
    def __init__(self, players):
        super(xTeam, self).__init__()
        self.players = players

        self.quality = sum(self.players, key=lambda x: x.overall) / 1089
        self.initial_hope = self.calculate_affinity() * self.quality

    def calculate_affinity(self):
        return 5

    def calculate_faults(self):
        num = 5  # TODO: calculate fault number
        return (1 - num/100)

    def calculate_cards(self):
        # Return cards
        pass

    def calculate_goals(self, hope):
        return int((hope/40)**2)
