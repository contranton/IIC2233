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
        jugadores = [['0', 'C. López', ' Camilo López', 'FC Barcelona',
                      'Spanish Primera División', 'Chile', '92'],
                     ['1', 'N.Kawas', 'Nebil Kawas', 'CD Palestino',
                      'Chilian Primera División', 'Chile', '95'],
                     ['2', 'J.Castro', 'Jaime Castro', 'Real Madrid CF',
                      'Spanish Primera División', 'Chile', '95'],
                     ['3', 'C.Ruz', 'Cristian Ruz', 'Audax italiano',
                      'Chilian Primera División', 'Chile', '95'],
                     ['4', 'R.Schilling', 'Ricardo Schilling',
                      'Paris Saint-Germain', 'French Ligue 1', 'Brazil', '90'],
                     ['20801', 'Cristiano Ronaldo',
                      'C. Ronaldo dos Santos Aveiro', 'Real Madrid CF',
                      'Spanish Primera División', 'Portugal', '94'],
                     ['158023', 'L. Messi', 'Lionel Messi', 'FC Barcelona',
                      'Spanish Primera División', 'Argentina', '93'],
                     ['190871', 'Neymar', 'Neymar da Silva Santos Jr.',
                      'Paris Saint-Germain', 'French Ligue 1', 'Brazil', '92'],
                     ['176580', 'L. Suárez', 'Luis Suárez', 'FC Barcelona',
                      'Spanish Primera División', 'Uruguay', '92'],
                     ['167495', 'M. Neuer', 'Manuel Neuer', 'FC Bayern Munich',
                      'German Bundesliga', 'Germany', '92'],
                     ['188545', 'R. Lewandowski', 'Robert Lewandowski',
                      'FC Bayern Munich', 'German Bundesliga', 'Poland', '91'],
                     ['193080', 'De Gea', 'David De Gea Quintana',
                      'Manchester United', 'English Premier League', 'Spain',
                      '90'], ['183277', 'E. Hazard', 'Eden Hazard', 'Chelsea',
                              'English Premier League', 'Belgium', '90'],
                     ['182521', 'T. Kroos', 'Toni Kroos', 'Real Madrid CF',
                      'Spanish Primera División', 'Germany', '90'],
                     ['167664', 'G. Higuaín', 'Gonzalo Higuaín', 'Juventus',
                      'Italian Serie A', 'Argentina', '90'],
                     ['155862', 'Sergio Ramos', 'Sergio Ramos García',
                      'Real Madrid CF', 'Spanish Primera División', 'Spain',
                      '90'], ['192985', 'K. De Bruyne', 'Kevin De Bruyne',
                              'Manchester City', 'English Premier League',
                              'Belgium', '89'],
                     ['192119', 'T. Courtois', 'Thibaut Courtois', 'Chelsea',
                      'English Premier League', 'Belgium', '89'],
                     ['184941', 'A. Sánchez', 'Alexis Sánchez', 'Arsenal',
                      'English Premier League', 'Chile', '89'],
                     ['177003', 'L. Modrić', 'Luka Modrić', 'Real Madrid CF',
                      'Spanish Primera División', 'Croatia', '89']]
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
