# Client
import sys
sys.path.append("..")

import socket

from threading import Thread

from libT06.netcode import MessageHandler
from client.gui import MainWindow

HOST = "localhost"
PORT = 3338


class Client():
    def __init__(self):
        """

        """
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((HOST, PORT))
        self.socket_handler = MessageHandler(sock)

        #self.gui_thread = Thread(target=MainWindow, daemon=True)

    def __del__(self):
        query = self.socket_handler.make_query("disconnect", None)
        self.socket_handler.query(query)
        super().__del__(self)

        
    def download_midi(self, title):
        query = self.socket_handler.make_query("download", (title,))
        midi = self.socket_handler.query(query, raw_bytes=True)
        with open(title, 'wb') as f:
            f.write(midi)


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication

   # app = QApplication(sys.argv)
    client = Client()
    import pdb; pdb.set_trace()

   # sys.exit(app.exec_())
