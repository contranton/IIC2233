from GUI.Interfaz import Window
from PyQt5.QtWidgets import QApplication

from random import randrange

from structs.players import xTeam, xPlayer, xPlayerGraph
from structs.xList import xList
from structs.xDict import xDict
from structs.xTournament import xTournament
from fileio import read_players


def get_teams(players):
    teams = xDict()
    for player in players:
        if player.club in teams.keys():
            try:
                teams[player.club].add_player(player)
            except ValueError:
                continue
        else:
            teams[player.club] = xTeam(player.club)
            teams[player.club].add_player(player)
    return teams.values()


class Juego:
    def __init__(self, small=True, real=True):
        self.user_team = xTeam("Tu equipo")
        self.real = real

        self.players = xDict()  # For internal use
        jugadores = xList()  # For GUI
        try:
            players = read_players(small)
        except IOError:
            print("No tienes el archivo .csv correspondiente"
                  "\nAbortando...")
            input()
            return
        print("Creando Jugadores...")
        i = 0
        for player in players:
            if i == 200:
                break
            self.players[player[2]] = xPlayer(*player)
            jugadores.append(player)
            i += 1
        print("Jugadores Creados...")

        # Affinity is not yet defined for unkown players
        # It will be calculated on a need-by-need basis as memory
        # requirements for complete storage are rather large
        self.affinity_graph = xPlayerGraph(self.players.values())

        self.teams = get_teams(self.players.values())

        equipos = map(lambda team: xList(team.name, len(team.players)),
                      self.teams)

        ### No cambiar esta línea
        self.gui = Window(self, jugadores, equipos)
        ###

    def cambio_jugador(self, j1, j2, en_cancha):
        # Screw y'all, dijeron que las posiciones
        # en la cancha no importaban >:(
        if en_cancha:
            return
        self.user_team.delete_player(j1)
        self.user_team.add_player(j2)
        self.user_team.all_calculated = False
        self.user_team.calculate_player_affinities(self.affinity_graph)
        self.gui.cambiar_esperanza(self.user_team.initial_hope)

    def entra_jugador(self, jugador: str):
        player = self.players[jugador]
        self.user_team.add_player(player)
        self.user_team.all_calculated = False
        self.user_team.calculate_player_affinities(self.affinity_graph)
        self.gui.cambiar_esperanza(self.user_team.initial_hope)

    def simular_campeonato(self, equipos):  # list[list[str, int]]):
        teams = xList()

        # Make teams and calculate affinities
        self.gui.resetear_resultados()
        self.gui.agregar_resultado("Simulando torneo...")
        for eq in equipos:
            calc_affinity = self.real

            if eq[0] == "Tu equipo":
                team = self.user_team
                if len(team.players) < 11:
                    continue
                calc_affinity = True
            else:
                team = xTeam(eq[0])

            self.gui.agregar_resultado(
                "Calculando afinidades para equipo " + eq[0])

            team.fill_random_players(self.players.values())

            # If team doesn't play in this championship, its players can
            # play for other teams
            for player in team.players:
                player.assigned = True

            if calc_affinity:
                team.calculate_player_affinities(self.affinity_graph)
            else:
                team.initial_hope = randrange(60, 90)
            teams.append(team)

        assert(len(teams) == 16)
        assert(all(map(lambda x: len(x.players) == 11, teams)) is True)

        # Simulate game
        tournament = xTournament(teams)
        tournament.simulate()
        self.tournament = tournament

        # Deassign assigned players
        for team in teams:
            if team.name == "Tu equipo":
                continue
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

        s = s.format(stage=self._phase_names[int(numero)],
                     teams="\n".join(teams),
                     winners="\n".join(winners),
                     losers="\n".join(losers))

        self.gui.resetear_respuestas()
        self.gui.agregar_respuesta(s)


# NO CAMBIAR NADA PARA ABAJO
def main(small, real):
    app = QApplication([])

    Juego(small, real)

    app.exec_()
