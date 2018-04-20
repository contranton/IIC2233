from GUI.Interfaz import Window
from PyQt5.QtWidgets import QApplication

from structs.players import xTeam, xPlayer
from structs.xList import xList
from structs.xDict import xDict
from structs.xTournament import xTournament


def read_players() -> xList:
    players = xList()
    with open("../players_db_chica.csv", 'r', encoding="utf-8") as f:
        print("Reading file...")
        lines = xList(*f.readlines())
        lines.pop(0)
        for line in lines:
            player = xList(*line.strip().split(","))
            players.append(player)
        print("File read finished")
    return players


class Juego:
    def __init__(self):
        self.user_team = xTeam("Mi equipo")

        self.players = xDict()  # For internal use
        jugadores = xList()  # For GUI
        for player in read_players():
            self.players[player[0]] = xPlayer(*player)
            jugadores.append(player)

        self.affinity_graph = None

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
        pass

    def entra_jugador(self, jugador: str):
        player = self.players[jugador]
        self.user_team.add_player(player)

    def simular_campeonato(self, equipos):  # list[list[str, int]]):
        teams = xList()

        for eq in equipos:
            team = xTeam(eq[0])
            print(team)
            team.fill_random_players(self.players.values())
            team.calculate_player_affinities(self.affinity_graph)
            for p in team.players:
                p.assigned = True
            teams.append(team)

        assert(all(map(lambda x: len(x.players) == 11, teams)) is True)

        # Simulate game
        tournament = xTournament(teams)
        tournament.simulate()
        self.tournament = tournament

        # Deassign assigned players
        for team in teams:
            for player in team.players.values():
                player.assigned = False

    def consulta_usuario(self):
        pass

    def consulta_equipo(self, nombre):
        pass

    def consulta_ganadores(self):
        pass

    def consulta_partido(self, id):
        pass

    def consulta_fase(self, numero):
        pass


#### NO CAMBIAR NADA PARA ABAJO
def main():
    app = QApplication([])
    try:
        a = Juego()
    except:
        import pdb
        pdb.pm()

    app.exec_()
