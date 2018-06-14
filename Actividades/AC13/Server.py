import socket
from json import dumps, loads
from random import randint
from threading import Thread
from time import sleep


DEFAULT_HOST = socket.gethostbyname('0.0.0.0')
DEFAULT_PORT = 3338

class Server:

    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT):
        """
        Esta clase representa a un cliente, el cual se conecta
        a un servidor en host:port. Ademas, puede enviar y recibir
        mensajes del servidor
        """

        self.methods = {'mover': self.move,
                        'crear': self.create}
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((host, port))
        sock.listen()
        self.connections = 0
        while True:
            client, addr = sock.accept()
            if self.connections < 1:
                self.connections += 1
                print("Connected to ", addr)
                Thread(target=self.handle_client, args=(client,), daemon=True).start()
            else:
                print("Refused connection to ", addr)
        sock.close()

    def handle_client(self, client):
        while True:
            data = client.recv(4096)
            if not data:
                break

            j_data = loads(data)
            print("Received ", j_data)
            order = j_data['orden']
            if order == 'desconectar':
                break
            else:
                foo = self.methods[order]
                foo(client, j_data)
        self.connections -= 1

    def create(self, client, j_dict):
        j_dict['posicion'] = tuple([randint(0, 500) for i in range(2)])

        data = dumps(j_dict).encode("utf-8")
        client.sendall(data)

    def move(self, client, j_dict):
        client.sendall(dumps(j_dict).encode("utf-8"))

if __name__ == '__main__':
    server = Server()
