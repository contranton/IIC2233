from fileio import read_players
from structs.xList import xList
from structs.players import xPlayer, xPlayerGraph


def consultas():
    players = xList()
    for p in read_players():
        players.append(xPlayer(*p))

    graph = xPlayerGraph(players)

    
