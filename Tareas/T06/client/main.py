# Client
import sys
sys.path.append("..")

import socket

from threading import Thread, Event
from PyQt5.QtCore import pyqtSignal, QObject

from libT06.netcode import MessageHandler
from client.gui import MainWindow

HOST = "localhost"
PORT = 3338


class Client(QObject):
    counter = 0

    signal_song_menu = pyqtSignal(bool)
    signal_midis_list = pyqtSignal(list, list)

    def __init__(self):
        super().__init__()
        Client.counter += 1
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((HOST, PORT))
        self.socket_handler = MessageHandler(Client.counter, sock)

        self.win = MainWindow(self.socket_handler.query)
        self.signal_midis_list.connect(self.win.update_midis)
        self.signal_song_menu.connect(self.win.song_menu)

        Thread(target=self.listen_wrapper, daemon=True).start()

    def __del__(self):
        try:
            self.socket_handler.query("disconnect", "")
        except AttributeError:  # Only in case connection has failed
            return
        self.socket_handler.socket.close()

    def listen_wrapper(self):
        try:
            self.listen()
        except Exception:
            import traceback as tb; tb.print_exc()
            print(f"ERROR: CLIENT HAS RESTARTED DUE TO EXCEPTION")
            Thread(target=self.listen_wrapper, daemon=True).start()
        
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
                self.handle_json_response(msg, header)

                # Handle midi data
            elif msg_type == 'midi':  # msg is midi as bytes
                self.handle_midi_response(msg, header)

    def handle_json_response(self, msg, header):
        content_type = msg['content_type']
        data = msg['data']
        if content_type == 'midis_list':
            edited = data['edited']
            available = data['available']
            self.signal_midis_list.emit(edited, available)
        elif content_type == 'edit_response':
            if not data["status"]:
                print(data["reason"])
            else:
                self.signal_song_menu.emit(data["can_edit"])
        elif content_type == 'connected_in_room':
            pass
        elif content_type == 'chat_initial':
            pass
        elif content_type == 'chat_message':
            pass

    def handle_midi_response(self, msg, header):
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
