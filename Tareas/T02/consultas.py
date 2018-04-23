from fileio import read_players
from structs.xDict import xDict
from structs.xList import xList
from structs.players import xPlayer, xPlayerGraph


def check_num():
    s = input()
    if not s.isnumeric or s != "q" or s!= "h":
        print("No ingresaste un numero")
        return check_num()
    return s

def do_input():
    print("Ingresa la ID de un jugador\n"
          "Ingresa 'q' para salir o 'h' para listar las "
          "IDs disponibles")
    s = input()
    return s

def consultas(small):
    players = xDict()
    in_players = read_players(small=small)

    print("Generando jugadores")
    for p in in_players:
        players[int(p[0])] = xPlayer(*p)
    ids = xList(*map(lambda p: p.ID, players.values()))
    print("Jugadores creados")

    print("Generando grafo de jugadores")
    graph = xPlayerGraph(players.values())
    print("Grafo terminado")

    s = do_input()
    while s != "q":
        if s == "h":
            print(ids)
            s = do_input()
            continue
        n = int(s)
        if n not in ids:
            print("No hay jugadores con esta ID")
            s = do_input()
            continue
        player = players[n]
        print("Calculando consultas.....")
        best = graph.get_best_friend(player)
        print("1/4")
        worst = graph.get_worst_friend(player)
        print("2/4")
        pop = graph.get_most_popular()
        print("3/4")
        star = graph.star_choice(player)
        star = star if star else "inexistente :("
        print("4/4")
        print("Consultas calculadas\n\n")
        t = "El jugador mas popular es {pop}\n"\
            "El mejor amigo de {player} es {best}.\n"\
            "Su peor amigo es {worst}\n"\
            "Su fichaje estrella es {star}\n\n"
        t = t.format(player=player.name,
                     best=best.name,
                     pop=pop.name,
                     star=star.name,
                     worst=worst.name)
        print(t)
        s = do_input()
