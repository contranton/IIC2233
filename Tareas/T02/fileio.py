from structs.xList import xList
from structs.xDict import xDict


def read_players(small=False) -> xList:
    players = xList()
    s = "../players_db"
    s += "_chica" if small else ""
    s += ".csv"
    with open(s, 'r', encoding="utf-8") as f:
        print("Reading file...")
        lines = xList(*f.readlines())
        lines.pop(0)
        for line in lines:
            player = xList(*line.strip().split(","))
            players.append(player)
        print("File read finished")
    return players
