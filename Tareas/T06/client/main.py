# Client
import socket

from threading import Thread
from PyQt5.QtCore import pyqtSignal, QObject

from netcode import MessageHandler
from gui import MainWindow

HOST = "localhost"
PORT = 3338


class Client(QObject):
    counter = 0

    # Signals for GUI updates
    signal_song_menu = pyqtSignal(bool)
    signal_midis_list = pyqtSignal(list, list)
    signal_midi_notes = pyqtSignal(dict)
    signal_connected_people = pyqtSignal(list)
    signal_new_messages = pyqtSignal(list)
    signal_username_response = pyqtSignal(dict)
    signal_server_crash = pyqtSignal()

    def __init__(self):
        super().__init__()
        Client.counter += 1
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((HOST, PORT))
        self.socket_handler = MessageHandler(Client.counter, sock)

        # Create GUI and connect signals to its functions
        self.win = MainWindow(self.socket_handler.query)
        self.signal_midis_list.connect(self.win.update_midis)
        self.signal_song_menu.connect(self.win.song_menu)
        self.signal_midi_notes.connect(self.win.load_notes)
        self.signal_connected_people.connect(self.win.update_connected)
        self.signal_new_messages.connect(self.win.new_messages)
        self.signal_username_response.connect(self.win.username_response)
        self.signal_server_crash.connect(self.win.server_crash_notice)

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
        except AttributeError:
            import traceback as tb; tb.print_exc()
            #print(f"ERROR: CLIENT HAS RESTARTED DUE TO EXCEPTION")
            Thread(target=self.listen_wrapper, daemon=True).start()
        
    def listen(self):
        """
        Handles content updates from server
        """
        while True:
            # Blocks until next server update is sent
            try:
                header, msg = self.socket_handler.recv()
            except ConnectionResetError:
                self.signal_server_crash.emit()
                break
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
                #print(data["reason"])
                pass
            else:
                self.signal_song_menu.emit(data["can_edit"])
        elif content_type == 'midi_notes':
            #print(data)
            self.signal_midi_notes.emit(data)
        elif content_type == 'username_response':
            self.signal_username_response.emit(data)
        elif content_type == 'connected_in_room':
            self.signal_connected_people.emit(data)
        elif content_type == 'chat_initial':
            pass
        elif content_type == 'chat_message':
            self.signal_new_messages.emit(data)

    def handle_midi_response(self, msg, header):
        title = header['descr']  # Song title
        with open(title + ".mid", 'wb') as f:
            f.write(msg)
        
if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    print("\n"*5)
    client = Client()
    sys.exit(app.exec_())
    #import pdb; pdb.pm()
