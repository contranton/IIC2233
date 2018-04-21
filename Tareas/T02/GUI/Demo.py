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
            for player in team.players:
                player.assigned = False

        self.update_resultados()

    def update_resultados(self):
        s = "Fase Eliminatoria:\n{}\nCuartos de Final:\n{}\n"\
            "Semi-Finales:\n{}\nRonda Tercer Lugar:\n{}\nFinal:\n{}"
        strs = xList()
        for level in self.tournament.bracket.values():
            s_lvl = ""
            for game in level.values():
                s_lvl += str(game) + "\n"
            strs.append(s_lvl)

        # Hack to remove the last game before we add the third roung
        strs.pop()

        # Remaining rounds
        strs.append(str(self.tournament.third_round_game) + "\n")
        strs.append(str(self.tournament.last_game))
        results = s.format(*strs)

        self.gui.resetear_resultados()
        self.gui.agregar_resultado(results)

    def consulta_usuario(self):
        raise NotImplementedError("User Team not yet integrated with tournament")

    def consulta_equipo(self, nombre):
        try:
            team = self.tournament.teams[nombre]
        except KeyError:
            return 

    def consulta_ganadores(self):

        T = self.tournament

        s = "1er lugar: {}\n2do lugar: {}\n3er lugar: {}"
        s = s.format(str(T.first), str(T.second), str(T.third))

        self.gui.resetear_respuestas()
        self.gui.agregar_respuesta(s)
        
    def consulta_partido(self, id):
        def _extract_cards(color, results):
            return sum(map(lambda x: x["Amarilla"], R1["cards"].values()))

        G = self.tournament.games[int(id)]
        R1 = G.results[G.team1.name]
        R2 = G.results[G.team2.name]

        cards_1 = xList(_extract_cards("Amarilla", R1),
                        _extract_cards("Roja", R1))
        cards_2 = xList(_extract_cards("Amarilla", R2),
                        _extract_cards("Roja", R2))
        
        s = "{game}\n\nGoles:\n  {t1}: {t1_g}\n  {t2}: {t2_g}\n\n"\
            "Faltas:\n  {t1}: {t1_f}\n  {t2}: {t2_f}\n\n"\
            "Tarjetas:\n  {t1}: {t1_y} amarillas, {t1_r} rojas"\
            "\n  {t2}: {t2_y} amarillas, {t2_r} rojas"
        s = s.format(game=str(G),
                     t1=G.team1, t1_g=R1["goals"],
                     t1_f=R1["faults"],
                     t1_y=cards_1[0], t1_r=cards_1[1],
                     t2=G.team2, t2_g=R2["goals"],
                     t2_y=cards_2[0], t2_r=cards_2[1],
                     t2_f=R2["faults"], t2_j=R2["cards"])

        self.gui.resetear_respuestas()
        self.gui.agregar_respuesta(s)

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
