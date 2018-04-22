from GUI.Interfaz import Window
from PyQt5.QtWidgets import QApplication

from structs.players import xTeam, xPlayer, xPlayerGraph
from structs.xList import xList
from structs.xDict import xDict
from structs.xTournament import xTournament
from fileio import read_players


class Juego:
    def __init__(self):
        self.user_team = xTeam("Tu equipo")

        self.players = xDict()  # For internal use
        jugadores = xList()  # For GUI
        for player in read_players():
            self.players[player[2]] = xPlayer(*player)
            jugadores.append(player)

        # Affinity is not yet defined for unkown players
        # It will be calculated on a need-by-need basis as memory
        # requirements for complete storage are rather large
        self.affinity_graph = xPlayerGraph(self.players.values())

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
            if eq[0] == "Tu equipo":
                team = self.user_team
            else:
                team = xTeam(eq[0])
            team.fill_random_players(self.players.values())
            team.calculate_player_affinities(self.affinity_graph)
            for p in team.players:
                p.assigned = True
            teams.append(team)

        assert(len(teams) == 16)
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
                s_lvl += str(game.id) + ": " + str(game) + "\n"
            strs.append(s_lvl)

        # Hack to remove the last game before we add the third roung
        strs.pop()

        # Remaining rounds
        strs.append("{x.id}: {x}".format(x=self.tournament.third_round_game)
                    + "\n")
        strs.append("{x.id}: {x}".format(x=self.tournament.last_game)
                    + "\n")
        results = s.format(*strs)

        self.gui.resetear_respuestas()
        self.gui.resetear_resultados()
        self.gui.agregar_resultado(results)

    def consulta_usuario(self):
        if "Tu equipo" not in self.tournament.teams.keys():
            self.gui.resetear_respuestas()
            self.gui.agregar_respuesta("Tu equipo no jugó en este campeonato")
            return

        self.consulta_equipo("Tu equipo")

    def consulta_equipo(self, nombre):
        try:
            team = self.tournament.teams[nombre]
        except KeyError:
            self.gui.resetear_respuestas()
            self.gui.agregar_respuesta("Nombre de equipo inválido")
            return

        games = self.tournament.find_team_games(team)

        last_phase = max(games.keys())
        last_game = games[last_phase]

        goals = xList(0, 0)  # index 0: scored, index 1: taken
        faults = 0
        cards = xList(0, 0)  # index 0: yellows, index 1: reds
        for game in games.values():
            opponent = game.team1 if game.team2 == team else game.team2
            R1 = game.results[team.name]
            R2 = game.results[opponent.name]

            goals[0] += R1["goals"]
            goals[1] += R2["goals"]

            faults += len(R1["faults"])

            cards[0] += self._extract_cards("Amarilla",  R1)
            cards[1] += self._extract_cards("Roja", R2)

        s_if_elim =\
            {True: "Fue eliminado por %s" % last_game.winner,
             False: "Ganó el campeonato!"}[self.tournament.first != team]

        s = "Equipo {team}\n\nLlegó hasta la fase '{last_phase}'"\
            "\n{if_elim}\n\nHizo un total de {goals_scored} goles y"\
            "\n   recibió {goals_taken} goles de sus oponentes.\n\nCometió"\
            " {n_faults} faltas.\n\nObtuvo {yellows} tarjetas amarillas\n  y "\
            "{reds} rojas."

        s = s.format(team=nombre,
                     last_phase=self._phase_names[last_phase],
                     if_elim=s_if_elim,
                     goals_scored=goals[0],
                     goals_taken=goals[1],
                     n_faults=faults,
                     yellows=cards[0],
                     reds=cards[1])

        self.gui.resetear_respuestas()
        self.gui.agregar_respuesta(s)

    def consulta_ganadores(self):

        T = self.tournament

        s = "1er lugar: {}\n2do lugar: {}\n3er lugar: {}"
        s = s.format(str(T.first), str(T.second), str(T.third))

        self.gui.resetear_respuestas()
        self.gui.agregar_respuesta(s)

    @staticmethod
    def _extract_cards(color, results):
        return sum(map(lambda x: x[color], results["cards"].values()))

    def consulta_partido(self, id):

        try:
            G = self.tournament.games[int(id)]
        except (ValueError, IndexError):
            self.gui.resetear_respuestas()
            self.gui.agregar_respuesta("ID de partido inválida")
            return
        R1 = G.results[G.team1.name]
        R2 = G.results[G.team2.name]

        cards_1 = xList(self._extract_cards("Amarilla", R1),
                        self._extract_cards("Roja", R1))
        cards_2 = xList(self._extract_cards("Amarilla", R2),
                        self._extract_cards("Roja", R2))

        faltas_1 = "\n   ".join(map(lambda x: x.name, R1["faults"]))
        faltas_2 = "\n   ".join(map(lambda x: x.name, R2["faults"]))

        s = "{game}\n\nGoles:\n  {t1}: {t1_g}\n  {t2}: {t2_g}\n\n"\
            "Faltas:\n- {t1}:\n   {t1_f}\n- {t2}:\n   {t2_f}\n\n"\
            "Tarjetas:\n  {t1}: {t1_y} amarillas, {t1_r} rojas"\
            "\n  {t2}: {t2_y} amarillas, {t2_r} rojas"
        s = s.format(game=str(G),
                     t1=G.team1, t1_g=R1["goals"],
                     t1_f=faltas_1,
                     t1_y=cards_1[0], t1_r=cards_1[1],
                     t2=G.team2, t2_g=R2["goals"],
                     t2_f=faltas_2,
                     t2_y=cards_2[0], t2_r=cards_2[1])

        self.gui.resetear_respuestas()
        self.gui.agregar_respuesta(s)

    _phase_names = xDict(xList(0, 1, 2, 3),
                         xList("Eliminatoria", "Cuartos de Final",
                               "Semi Final", "Final"))

    def consulta_fase(self, numero):
        try:
            phase = self.tournament.bracket[int(numero)]
        except (ValueError, KeyError):
            self.gui.resetear_respuestas()
            self.gui.agregar_respuesta("Numero de fase inválida")
            return

        s = "{stage}\n\nPartidos:\n{teams}\n\nGanadores:\n{winners}\n\n"\
            "Perdedores:\n{losers}"
        teams = xList()
        winners = xList()
        losers = xList()
        for game in phase.values():
            teams.append(str(game))
            winners.append(str(game.winner))
            losers.append(str(game.loser))

        s = s.format(stage=self._phase_names[numero],
                     teams="\n".join(teams),
                     winners="\n".join(winners),
                     losers="\n".join(losers))


        self.gui.resetear_respuestas()
        self.gui.agregar_respuesta(s)

#### NO CAMBIAR NADA PARA ABAJO
def main():
    app = QApplication([])

    a = Juego()

    app.exec_()
