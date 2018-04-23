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


def small_or_large_db():
    print("Usar base de datos pequeña o grande?\n"
          "1. Pequeña (N=199)\n"
          "2. Grande (N=5500)\n")
    return True if get_choice(xList(1, 2)) == 1 else False


def use_slow_mode():
    print("Jugar campeonato en modo simple o real?\n"
          "Modo simple usa esperanzas fijas para cada equipo"
          " oponente a modo de no re-calcularlas, y solo realiza"
          " el calculo para el equipo jugador.\n"
          "Modo real ignora esa esperanza fija y calcula la "
          "esperanza para todos los equipos, lo que se demorara"
          "mucho incluso si utilizas la base de datos pequeña\n\n"
          "Calcular la afinidad para:\n"
          "1. Solo el equipo jugador (Rapido)\n"
          "2. Todos los equipos (Leeeeeeeento)\n")
    return False if get_choice(xList(1, 2)) == 1 else True


if __name__ == '__main__':
    os.chdir("GUI")
    print("Programming Evolution Soccer\n"
          "1. Consulta sobre jugadores\n"
          "2. Jugar campeonato")
    option = get_choice(xList(1, 2))
    if option == 1:
        consultas(small=small_or_large_db())
    elif option == 2:
        main(real=use_slow_mode(),
             small=small_or_large_db())
