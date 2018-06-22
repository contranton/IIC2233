# Server
import sys
sys.path.append("..")

import socket

from threading import Thread

from libT06.netcode import MessageHandler
from server.midi import get_midis

HOST = socket.gethostbyname('0.0.0.0')
PORT = 3338
print(HOST, PORT)


class MidiDatabase():
    """
    Stores midi in tuple (midi: MIDIFile, available: bool)
    """
    _midis = {name: (midi, True) for (midi, name, _) in get_midis()}

    @property
    def midis(self):
        return {name: midi for (name, (midi, _)) in self._midis.items()}

    @property
    def availables(self):
        return {name: midi for (name, (midi, available)) in self._midis.items()
                if available}

    @property
    def edited(self):
        return {name: midi for (name, (midi, available)) in self._midis.items()
                if not available}

    @property
    def names(self):
        return list(self.midis.keys())


class Server():

    def __init__(self):
        """

        """
        self.action_map = {"download": self.download_midi}
        self.db = MidiDatabase()
        print(f"Available midis: {self.db.midis}")

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((HOST, PORT))

        # Running server as a thread lets us kill the program in
        # console without having to shut down the entire console
        Thread(target=self.listen, daemon=True).start()

    def __del__(self):
        self.sock.close()

    def listen(self):
        self.sock.listen()
        while True:
            # Block until connection is received
            client, addr = self.sock.accept()

            # Run each client handler on its own thread
            Thread(target=self.handle_client,
                   args=(client, addr),
                   daemon=True).start()

    def handle_client(self, client, addr):
        print(f"New connection from {addr}")
        handler = MessageHandler(addr, client)
        self.send_midi_list(handler)
        while True:
            # Get message
            header, msg = handler.recv()
            print(f"Received '{msg}'")
            if not msg:  # Only in case of errors
                continue

            # Apply action given message.
            # Action is a single string identifying the function while
            # data is a tuple containing all arguments said function
            # requires.
            action = msg["action"]
            if action == "disconnect":
                break
            data = msg["data"]
            self.action_map[action](handler, *data)

        print(f"Ended connection from {addr}")

    def update_midis_status(self):
        pass

    def send_midi_list(self, client_handler):
        msg = {"content_type": "midis_list",
               "data": {"edited": [name for name in
                                   self.db.edited.keys()],
                        "available": [name for name in
                                      self.db.availables.keys()]}
               }
        client_handler.send_message(msg, descr='midi_list')

    def download_midi(self, client_handler, midi_name):
        midi_bytes = self.db.midis[midi_name].to_bytes()
        client_handler.send_message(midi_bytes,
                                    msg_type='midi',
                                    descr=midi_name)


if __name__ == '__main__':
    # Run server
    server = Server()
    # Loop to receive system signals, e.g. KeyboardInterrupt
    try:
        while True:
            continue
    except:
        #import pdb; pdb.pm()
        pass
