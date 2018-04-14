from structs.xList import xList
from structs.xDict import xDict
from structs.players import Player


def read_players():
    players = xDict()
    with open("players_db.csv", 'r') as f:
        lines = xList(*f.readlines())
        print("Reading file...")
        for line in lines:
            player = Player(*line.split(","))
            players[player.ID] = player
    return players
