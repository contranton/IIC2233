# Server
import sys
sys.path.append("..")

import socket

from threading import Thread

from libT06.netcode import MessageHandler
from server.midi import get_midis, MIDIFile

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

    def create_midi(self, title):
        # False as the new midi is now being edited
        self._midis[title] = (MIDIFile(), False)


class Server():

    def __init__(self):
        """

        """
        self.action_map = {"download": self.download_midi,
                           "create": self.create_midi,
                           "edit": self.edit_midi}
        self.db = MidiDatabase()
        print(f"Available midis: {self.db.midis}")

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((HOST, PORT))

        # Running server as a thread lets us kill the program in
        # console without having to shut down the entire console
        Thread(target=self.listen, daemon=True).start()

        self.signed_in_users = []

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

    def edit_midi(self, client_handler, username, title):
        
        msg = {"content_type": "edit_response",
               "data": None}
        print(title)
        print(self.db.availables)
        
        if username in self.signed_in_users:
            msg["data"] = {"status": False,
                           "reason": "Username taken"}
        else:
            msg["data"] = {"status": True,
                           "can_edit": (title in self.db.availables)}

        client_handler.send_message(msg, descr='edit_response')
        
    def create_midi(self, client_handler, username, title):
        """
        """
        self.db.create_midi(title)

        msg = {"content_type": "edit_response",
               "data": None}
        
        if username in self.signed_in_users:
            msg["data"] = {"status": False,
                           "reason": "Username taken"}
        elif len(title) < 6:
            msg["data"] = {"status": False,
                           "reason": "Title too short"}
        else:
            msg["data"] = {"status": True,
                           "can_edit": True}

        client_handler.send_message(msg, descr='create_response')



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
