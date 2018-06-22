from PyQt5.QtWidgets import (QApplication, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QWidget,
                             QGridLayout, QLineEdit, QListWidget,
                             QComboBox, QSpinBox)
from PyQt5.QtCore import Qt


class MainWindow(QWidget):
    """
    """
    def __init__(self, query):
        super().__init__()

        # Comms sender for querying server. Recvs are done in the
        # main client routine, never here
        self.query = query

        # Layout
        vdiv = QVBoxLayout()

        # 1: Top Label
        vdiv.addWidget(QLabel("<b>PrograBand</b>"))

        # 2: Username input
        user_input = QHBoxLayout()
        user_input.addWidget(QLabel("Username"))
        self.user_text_input = QLineEdit()
        self.user_text_input.setPlaceholderText("Enter your username here...")
        self.user_text_input.setMaximumHeight(30)
        user_input.addWidget(self.user_text_input)
        vdiv.addLayout(user_input)

        # 3: Song lists
        song_lists = QHBoxLayout()
        edited = QVBoxLayout()
        ready = QVBoxLayout()

        edited.addWidget(QLabel("Songs being edited"))
        self.edited = QListWidget()
        edited.addWidget(self.edited)
        song_lists.addLayout(edited)

        ready.addWidget(QLabel("Songs available"))
        self.ready = QListWidget()
        ready.addWidget(self.ready)
        song_lists.addLayout(ready)

        vdiv.addLayout(song_lists)

        # 4: Actions
        actions = QHBoxLayout()
        self.edit_button = QPushButton("Edit")
        self.edit_button.pressed.connect(self.edit)
        self.download_button = QPushButton("Download")
        self.download_button.pressed.connect(self.download)
        actions.addWidget(self.edit_button)
        actions.addWidget(self.download_button)
        vdiv.addLayout(actions)

        # 5: New song
        new_song = QVBoxLayout()
        new_song.addWidget(QLabel("New Song"))
        self.new_song_input = QLineEdit()
        self.new_song_input.setPlaceholderText("Enter name of the new song...")
        new_button = QPushButton("Create song")
        new_button.pressed.connect(self.new_song)
        new_song.addWidget(new_button)
        vdiv.addLayout(new_song)

        vdiv.setAlignment(Qt.AlignCenter)
        self.setLayout(vdiv)
        self.show()

    def edit(self):
        pass

    def download(self):
        pass

    def new_song(self):
        pass

    def update_midis(self, edited_midis, available_midis):
        self.edited.clear()
        self.ready.clear()
        self.edited.addItems(edited_midis)
        self.ready.addItems(available_midis)


class EditingWindow(QWidget):
    def __init__(self, is_editor):
        super().__init__()
        self.setWindowTitle("Editing Song")
        hdiv = QHBoxLayout()

        # 1: Note editing menu
        # TODO: Make edition more ergonomic
        if is_editor:
            note_menu = QVBoxLayout()

            self.pitch = QComboBox()
            self.pitch.insertItems(0, "do re mi fa sol la si".split(" "))
            note_menu.addWidget(self.pitch)
            self.scale = QSpinBox()
            self.scale.setRange(0, 10)
            note_menu.addWidget(self.scale)
            self.velocity = QComboBox()
            self.velocity.insertItems(0, "pppp ppp pp p mp "
                                      "mf f ff fff ffff".split(" "))
            self.velocity.setCurrentIndex(5)
            note_menu.addWidget(self.velocity)
            self.duration = QComboBox()
            self.duration.insertItems(0, "4 2 1 1/2 1/4 1/8 1/16".split(" "))
            self.duration.setCurrentIndex(4)
            note_menu.addWidget(self.duration)

            note_menu.addStretch()

            hdiv_buttons = QHBoxLayout()
            btn_add = QPushButton("Add Note")
            btn_add.pressed.connect(self.add_note)
            btn_del = QPushButton("Delete Note")
            btn_del.pressed.connect(self.delete_note)
            hdiv_buttons.addWidget(btn_add)
            hdiv_buttons.addWidget(btn_del)

            note_menu.addLayout(hdiv_buttons)

            note_menu.addStretch()

            done_btn = QPushButton("Finish")
            done_btn.pressed.connect(self.finished)
            note_menu.addWidget(done_btn)

            hdiv.addLayout(note_menu)

        # 2: Note display list
        self.note_list = QListWidget()

        hdiv.addWidget(self.note_list)

        # 3: Chat & user list
        vdiv_chat = QVBoxLayout()

        self.chat = QListWidget()
        vdiv_chat.addWidget(self.chat)

        type_div = QHBoxLayout()
        self.chat_field = QLineEdit()
        self.chat_field.setPlaceholderText("Type your message here...")
        chat_send = QPushButton("Send")
        chat_send.pressed.connect(self.send_message)
        type_div.addWidget(self.chat_field)
        type_div.addWidget(chat_send)
        vdiv_chat.addLayout(type_div)

        self.connected = QListWidget()
        vdiv_chat.addWidget(self.connected)

        hdiv.addLayout(vdiv_chat)

        # Main layout
        self.setLayout(hdiv)
        self.show()

    def load_chat(self):
        pass

    def add_note(self):
        pass

    def delete_note(self):
        pass

    def finished(self):
        pass

    def send_message(self):
        pass


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    win = EditingWindow(is_editor=False)
    sys.exit(app.exec_())
