# Server
import sys
sys.path.append("..")

import socket

from threading import Thread

from lib.netcode import MessageHandler
from server.midi import get_midis

HOST = socket.gethostbyname('0.0.0.0')
PORT = 3338
print(HOST, PORT)


class MidiDatabase():
    midis = {name: midi for (midi, name, _) in get_midis()}

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
        handler = MessageHandler(client)
        while True:
            # Get message
            msg = handler.recv()
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

    def download_midi(self, client_handler, midi_name):
        midi_bytes = self.db.midis[midi_name].to_bytes()
        client_handler.send_message(midi_bytes, raw_bytes=True)


if __name__ == '__main__':
    # Run server
    server = Server()

    # Loop to receive system signals, e.g. KeyboardInterrupt
    try:
        while True:
            continue
    except:
        import pdb; pdb.set_trace()
