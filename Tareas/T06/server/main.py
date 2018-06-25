# Server
import socket
import time
import os
import json

from threading import Thread

from netcode import MessageHandler
from midi import get_midis, MIDIFile, MIDITrack

HOST = socket.gethostbyname("localhost")
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

    def get_midi_from_viewer(self, viewer):
        for name, d in self._midis.items():
            if d['editor'] == viewer:
                return name
            if viewer in d['spectators']:
                return name

    def create_midi(self, title, editor):
        midi = MIDIFile()
        midi.add_track(MIDITrack(0, midi.time_div))
        self._midis[title] = {'file': midi,
                              'editor': editor,
                              'spectators': []}

    def set_editor(self, title, editor):
        self._midis[title]['editor'] = editor

    def get_editor(self, title):
        return [self._midis[title]['editor']]

    def get_spectators(self, title):
        return self._midis[title]['spectators']

    def clear_viewer(self, editor):
        for name in self._midis:
            if self._midis[name]['editor'] == editor:
                self._midis[name]['editor'] = None
                break
            if editor in self._midis[name]['spectators']:
                self._midis[name]['spectators'].remove(editor)

    def add_spectator(self, title, spectator):
        self._midis[title]['spectators'].append(spectator)

    def get_notes_list(self, title):
        midi = self.midis[title]
        return midi.get_notes()

    def save_files(self):
        for name, midi in self.midis.items():
            with open(f"midis/{name}.mid", 'wb') as file:
                file.write(midi.to_bytes())


class Server():

    def __init__(self):
        """

        """
        self.n = 0

        self.action_map = {"download": self.download_midi,
                           "create": self.create_midi,
                           "edit": self.edit_midi,
                           "finished_editing": self.finish_edit,
                           "add_note": self.add_note,
                           "delete_note": self.delete_note,
                           "validate": self.validate_username,
                           "chat_send": self.new_message,
                           "add_track": self.add_track}
        self.db = MidiDatabase()
        self.load_chat()

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((HOST, PORT))

        
        # Running server as a thread lets us kill the program in
        # console without having to shut down the entire console
        Thread(target=self.listen, daemon=True).start()

        self.all_clients = []

        # Username: {'comm_id': str, 'midi': str, 'socket': socket}
        self.signed_in_users = {}

    def __del__(self):
        self.db.save_files()
        self.sock.close()

    def listen(self):
        self.sock.listen()
        MessageHandler.t_print("Time", "Client", "Action", "Details")
        while True:
            # Block until connection is received
            client, addr = self.sock.accept()

            # Run each client handler on its own thread
            Thread(target=self.handle_client,
                   args=(client, addr),
                   daemon=True).start()

    def handle_client(self, client, addr):
        self.n += 1
        handler = MessageHandler(self.n, client)
        handler.log("connected", addr)
        self.all_clients.append(handler)
        self.send_midi_list(handler)
        while True:
            # Get message
            try:
                header, msg = handler.recv()
            except ConnectionError:
                break
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

        # We must remove client as an editor if he crashes so
        # that others may edit
        username = self.username_from_comm(handler.id_)
        if username:
            # User was editing at the time of crash
            self.finish_edit(handler, username)

        self.all_clients.remove(handler)
        self.sign_out(handler.id_)
        handler.log("disconnect", addr)

    def validate_username(self, client_handler, username):
        valid = True
        if len(username) < 6:
            valid = False
            reason = "Username too short"
        if username in self.signed_in_users:
            valid = False
            reason = "Username already in use"

        msg = {'content_type': 'username_response',
               'data': {'valid': valid}}
        if not valid:
            msg['data']['reason'] = reason
        else:
            self.sign_in(client_handler, username)

        client_handler.send_message(msg, descr=username)

    def username_from_comm(self, comm_id):
        for user, (c_id, _, _) in self.signed_in_users.items():
            if c_id == comm_id:
                return user
        return None

    def sign_in(self, handler, username):
        self.signed_in_users[username] = {'comm_id': handler.id_,
                                          'midi': None,
                                          'socket': handler}

    def sign_out(self, comm_id):
        for user, vals in self.signed_in_users.items():
            if comm_id == vals['comm_id']:
                self.signed_in_users.pop(user)
                break

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

        msg["data"] = {"status": True,
                       "can_edit": can_edit}

        # Send edit response to enable client GUI creation
        self.signed_in_users[username]['midi'] = title
        client_handler.send_message(msg, descr='edit_response')
        if can_edit:
            self.db.set_editor(title, username)
        else:
            self.db.add_spectator(title, username)

        # Update midi list
        self.push_to_all_clients(self.send_midi_list)

        # Send notes and chat to editor and spectators
        self.sync_notes(title)
        self.sync_chat(title)

        # Send list of connected people to all users in room
        self.sync_users(title)

    def create_midi(self, client_handler, username, title):
        """
        """

        msg = {"content_type": "edit_response",
               "data": None}

        if len(title) < 6:
            msg["data"] = {"status": False,
                           "reason": "Title too short"}
        else:
            self.db.create_midi(title, client_handler.id_)
            self.db.set_editor(title, username)
            self.chat[title] = []
            self.signed_in_users[username]['midi'] = title
            msg["data"] = {"status": True,
                           "can_edit": True}

        client_handler.send_message(msg, descr='create_response')

        self.sync_users(title)

        self.push_to_all_clients(self.send_midi_list)

    def new_message(self, client_handler, username, message):
        time_ = time.strftime("%y/%m/%d - %H:%M:%S", time.localtime())
        msg = f"{time_} - {username}: {message}"
        title = self.db.get_midi_from_viewer(username)
        self.chat[title].append(msg)
        self.sync_chat(title)

    def finish_edit(self, client_handler, username):
        self.db.clear_viewer(username)
        self.push_to_all_clients(self.send_midi_list)

        title = self.db.get_midi_from_viewer(username)
        self.sync_users(title)

    def add_note(self, client_handler, username, index, track, pitch,
                 scale, velocity, duration, dotted):
        title = self.db.get_midi_from_viewer(username)
        midi = self.db.midis[title]
        midi.tracks[track].add_note(index, pitch, scale, velocity,
                                    duration, dotted)
        self.sync_notes(title)

    def delete_note(self, client_handler, username, index, track):
        title = self.db.get_midi_from_viewer(username)
        midi = self.db.midis[title]
        midi.tracks[track].delete_note(index)

        self.sync_notes(title)

    def add_track(self, client_handler, username):
        title = self.db.get_midi_from_viewer(username)
        midi = self.db.midis[title]
        N = midi.tracks[-1].number + 1
        midi.add_track(MIDITrack(N, midi.time_div))

        self.sync_notes(title)
        
    def sync_notes(self, title):
        notes = self.db.get_notes_list(title)
        self.push_to_viewers(title, self.send_notes, notes)

    def sync_users(self, title):
        viewers = [user for user, val in self.signed_in_users.items()
                   if val['midi'] == title]
        self.push_to_viewers(title, self.send_users, viewers)

    def sync_chat(self, title):
        chat = self.chat[title]
        self.push_to_viewers(title, self.send_chat, chat)

    def send_chat(self, client_handler, chat):
        msg = {'content_type': 'chat_message',
               'data': chat}
        client_handler.send_message(msg, descr='chat')

    def send_users(self, client_handler, viewers):
        msg = {'content_type': "connected_in_room",
               'data': viewers}
        client_handler.send_message(msg, descr='connected_users')

    def send_notes(self, client_handler, notes):
        msg = {'content_type': "midi_notes",
               'data': notes}
        client_handler.send_message(msg, descr='song_notes')

    def push_to_viewers(self, title, foo, *data):
        viewers = [dat['socket'] for dat in self.signed_in_users.values()
                   if dat['midi'] == title]
        #import pdb; pdb.set_trace()

        for socket in viewers:
            foo(socket, *data)

    def push_to_all_clients(self, foo, *data):
        for client_handler in self.all_clients:
            foo(client_handler, *data)

    def load_chat(self):
        if not os.path.exists("chats.json"):
            self.chat = {title: [] for title in self.db.midis.keys()}
            return
        with open("chats.json", 'rb') as file:
            data = json.loads(file.read().decode("utf-8"))
            self.chat = data
            
    def save(self):
        self.db.save_files()
        with open("chats.json", 'wb') as file:
            data = json.dumps(self.chat).encode("utf-8")
            file.write(data)


def debug(type, value, tb):
    import traceback, pdb
    # we are NOT in interactive mode, print the exception...
    traceback.print_exception(type, value, tb)
    # ...then start the debugger in post-mortem mode.
    # pdb.pm() # deprecated
    pdb.post_mortem(tb) # more "modern"


if __name__ == '__main__':
    import sys
    sys.excepthook = debug

    # Run server
    server = Server()

    # Loop to receive system signals, e.g. KeyboardInterrupt
    try:
        while True:
            continue
    except KeyboardInterrupt:
        pass
    finally:
        server.save()
