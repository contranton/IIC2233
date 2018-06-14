import socket
from threading import Thread
from time import sleep

host = ''
port = 12345

class Server():

    def __init__(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, port))
        sock.listen(5)
        while True:
            client, addr = sock.accept()
            print("Connection ", addr)
            Thread(target=server_handler, args=(client,), daemon=True).run()


def server_handler(client):
    while True:
        data = client.recv(4096)
        if not data:
            break
        print(f"Received {data} from client")
        resp = b"HELLO DUDE\n"
        client.sendall(resp)


class Client():

    def __init__(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        for i in range(5):
            sleep(1)
            sock.sendall(b"HELLO WORLD")
        sock.sendall("")
        sock.close()


if __name__ == '__main__':
    server = Server()
    client = Client()
