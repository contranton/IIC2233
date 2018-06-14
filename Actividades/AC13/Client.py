import socket
from json import dumps, loads
import sys
from threading import Thread
from time import sleep
from ventana_principal import MiVentana, QApplication

# SE DEBE OBTENER ESTA IP A PARTIR DE LA DADA POR EL SERVIDOR
DEFAULT_HOST = "192.168.43.91"
DEFAULT_PORT = 3338


class Client:

    def __init__(self, host=None, port=None):
        """
        Esta clase representa a un cliente, el cual se conecta 
        a un servidor en host:port. Ademas, puede enviar y recibir 
        mensajes del servidor
        """
        self.ventana = MiVentana(self.pedir_mover, self.desconectar)

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.sock.settimeout(5)
        self.sock.connect((host, port))

        self.sock.sendall(dumps({'orden': 'crear'}).encode('utf-8'))
        data = loads(self.sock.recv(4096))
        self.ventana.agregar_mi_personaje(*data['posicion'])

    def pedir_mover(self, x, y):
        """
        Esta función se llama cada vez que se aprieta una tecla, entregando la
        posición x, y a la que se deberia mover. En este paso deberían enviarle
        un mensaje al servidor indicando que se quiere mover el personaje a la
        posición x, y
        """
        data = dumps({'orden': 'mover', 'posicion': (x, y)})
        self.sock.sendall(data.encode("utf-8"))
        data = loads(self.sock.recv(4096))
        self.ventana.actualizar_posicion_personaje(*data['posicion'])
        print(x, y)

    def desconectar(self):
        """
        Esta función se llama cuando se cierra la interfaz. En este paso
        deberían enviarle un mensaje al servidor indicando que se van a
        desconectar y manejar la desconexion del cliente.
        """
        self.sock.sendall(dumps({'orden': 'desconectar'}).encode("utf-8"))



if __name__ == '__main__':
    def hook(type, value, traceback):
        print(type)
        print(value)
        print(traceback)
    sys.__excepthook__ = hook
    app = QApplication([])
    client = Client(DEFAULT_HOST, DEFAULT_PORT)
    app.exec_()
