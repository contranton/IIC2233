import os

from GUI.Demo import main
from structs.xList import xList
from consultas import consultas


def get_choice(choices):
    try:
        n = int(input())
    except ValueError:
        print("Input invalido")
        return get_choice(choices)
    if n not in choices:
        print("Valor no en rango legal")
        return get_choice(choices)
    return n


if __name__ == '__main__':

    print("Programming Evolution Soccer\n"
          "1. Consulta sobre jugadores\n"
          "2. Jugar campeonato")
    option = get_choice(xList(1, 2))
    if option == 1:
        consultas()
    elif option == 2:
        os.chdir("GUI")
        print(
            "Jugar campeonato en modo simple o real?\n"
            "Calcular la afinidad para:"
            "1. Solo el equipo jugador (Rapido)"
            "2. Todos los equipos (Leeeeeeeento)")
        option = get_choice(xList(1, 2))
        if option == 1:
            main(simple=True)
        elif option == 2:
            main(simple=False)
