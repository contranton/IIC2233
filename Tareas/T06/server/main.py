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
    _midis = {name: {'file': midi,
                     'editor': None,
                     'spectators': []}
              for (midi, name, _) in get_midis()}

    @property
    def midis(self):
        return {name: d['file'] for (name, d) in self._midis.items()}

    @property
    def availables(self):
        return {name: d['file'] for (name, d) in self._midis.items()
                if not d['editor']}

    @property
    def edited(self):
        return {name: d['file'] for (name, d) in self._midis.items()
                if d['editor']}

    @property
    def names(self):
        return list(self.midis.keys())

    def get_midi_from_editor(self, editor):
        for name, d in self._midis.items():
            if d['editor'] == editor:
                return name

    def create_midi(self, title, editor):
        # False as the new midi is now being edited
        self._midis[title] = {'file': MIDIFile(),
                              'editor': editor}

    def set_editor(self, title, editor):
        self._midis[title]['editor'] = editor

    def get_editor(self, title):
        return self._midis[title]['editor']

    def get_spectators(self, title):
        return self._midis[title]['spectators']

    def clear_editor(self, editor):
        for name in self._midis:
            if self._midis[name]['editor'] == editor:
                self._midis[name]['editor'] = None

    def add_spectator(self, client_socket):
        pass

    def get_notes_list(self, title):
        pass


class Server():

    def __init__(self):
        """

        """
        self.action_map = {"download": self.download_midi,
                           "create": self.create_midi,
                           "edit": self.edit_midi,
                           "finished_editing": self.finish_edit,
                           "add_note": self.add_note}
        self.db = MidiDatabase()
        print(f"Available midis: {self.db.midis}")

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((HOST, PORT))

        # Running server as a thread lets us kill the program in
        # console without having to shut down the entire console
        Thread(target=self.listen, daemon=True).start()

        self.all_clients = []
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
        self.all_clients.append(handler)
        self.send_midi_list(handler)
        while True:
            # Get message
            try:
                header, msg = handler.recv()
            except socket.exceptions.ConnectionError:
                break
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

        self.all_clients.remove(client)
        print(f"Ended connection from {addr}")

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

        can_edit = title in self.db.availables

        if username in self.signed_in_users:
            msg["data"] = {"status": False,
                           "reason": "Username taken"}
        else:
            msg["data"] = {"status": True,
                           "can_edit": can_edit}

        if can_edit:
            self.db.set_editor(title, client_handler.comm_id)

        self.push_to_all_clients(self.send_midi_list)
        client_handler.send_message(msg, descr='edit_response')

    def create_midi(self, client_handler, username, title):
        """
        """
        self.db.create_midi(title, client_handler.comm_id)

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

        self.push_to_all_clients(self.send_midi_list)
        client_handler.send_message(msg, descr='create_response')

    def finish_edit(self, client_handler):
        self.db.clear_editor(client_handler.comm_id)
        self.push_to_all_clients(self.send_midi_list)

    def add_note(self, client_handler, index, track, pitch, scale,
                 velocity, duration):
        title = self.db.get_midi_from_editor(client_handler.comm_id)
        self.db.midis[title].tracks[track].add_note(index, pitch,
                                                    scale, velocity, duration)
        self.sync_notes(title)

    def sync_notes(self, title):
        notes = self.db.get_notes_list(title)
        clients_viewing = [self.db.get_editor(title) +
                           self.db.get_spectators(title)]
        self.push_to_all_clients(self.send_notes, clients_viewing, notes)

    def send_notes(self, client_handler, viewers, notes):
        if client_handler.comm_id not in viewers:
            return
        client_handler.send_message("midi_notes", notes)

    def push_to_all_clients(self, foo, *data):
        for client_handler in self.all_clients:
            foo(client_handler, *data)


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
