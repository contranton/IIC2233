# Client
import sys
sys.path.append("..")

import socket

from threading import Thread, Lock

from libT06.netcode import MessageHandler
from client.gui import MainWindow

HOST = "localhost"
PORT = 3338


class Client():
    counter = 0

    def __init__(self):
        Client.counter += 1
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((HOST, PORT))
        self.socket_handler = MessageHandler(Client.counter, sock)

        self.win = MainWindow(self.socket_handler.query)

        Thread(target=self.listen, daemon=True).start()

    def __del__(self):
        try:
            self.socket_handler.query("disconnect", "")
        except AttributeError:  # Only in case connection has failed
            return
        self.socket_handler.socket.shutdown()

    def listen(self):
        """
        Handles content updates from server
        """
        while True:
            # Blocks until next server update is sent
            header, msg = self.socket_handler.recv()
            # Call the appropiate method based on the data
            msg_type = header['type']
            if msg_type == 'json':
                content_type = msg['content_type']
                data = msg['data']
                if content_type == 'midis_list':
                    edited = data['edited']
                    available = data['available']
                    self.win.update_midis(edited_midis=edited,
                                          available_midis=available)
                elif content_type == 'connected_in_room':
                    pass
                elif content_type == 'chat_initial':
                    pass
                elif content_type == 'chat_message':
                    pass
            elif msg_type == 'midi':  # msg is midi as bytes
                title = header['descr']  # Song title
                with open(title, 'wb') as f:
                    f.write(msg)


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    print("\n"*5)
    client = Client()
    sys.exit(app.exec_())
    #import pdb; pdb.pm()
