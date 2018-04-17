from PyQt5.QtWidgets import QApplication

from GUI.Interfaz import Window

from structs.xTournament import xTournament

def read_players():
    players = xList()
    with open("players_db.csv", 'r') as f:
        lines = xList(*f.readlines())
        print("Reading file...")
        for line in lines:
            player = xList(*line.split(","))
            players.append(player)
    return players

def make_teams():
    pass


class Juego:
    def __init__(self):
        jugadores = read_players()
        equipos = [('Super Campeones', 300), ('FC Barcelona', 200),
                   ('Real Madrid', 180),
                   ('Ayudantes FC', 20000), ('Alumnos FC', 5),
                   ('UC', 130), ('U Chile', 130),
                   ('Cobreloa', 110), ('Bad Bunny FC', 15),
                   ('2+2 = 5 FC', 125), ('Blank', 1200),
                   ('!"#$%&/(', 190), ('Ra ra rasputin', 200),
                   ('Arjona', 22), ('No u', 144)]


        ### No cambiar esta línea
        self.gui = Window(self, jugadores, equipos)
        ###

    def cambio_jugador(self, j1, j2, en_cancha):
        print("Executed function 'cambio_jugador'")

    def entra_jugador(self, jugador):
        print("Executed function 'entra_jugador'")

    def simular_campeonato(self, equipos):
        print("Executed function 'simular_campeonato'")

        import ipdb; ipdb.set_trace()
        T = xTournament(equipos)

    def consulta_usuario(self):
        print("Executed function 'consulta_usuario'")

    def consulta_equipo(self, nombre):
        print("Executed function 'consulta_equipo'")

    def consulta_ganadores(self):
        print("Executed function 'consulta_ganadores'")

    def consulta_partido(self, id):
        print("Executed function 'consulta_partido'")

    def consulta_fase(self, numero):
        print("Executed function 'consulta_fase'")


#### NO CAMBIAR NADA PARA ABAJO
if __name__ == '__main__':
    app = QApplication([])

    a = Juego()

    app.exec_()
