from PyQt5.QtWidgets import (QApplication, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QWidget,
                             QGridLayout, QLineEdit, QListWidget,
                             QComboBox, QSpinBox, QMessageBox,
                             QTextEdit, QCheckBox)
from PyQt5.QtCore import Qt


class MainWindow(QWidget):
    """
    """
    def __init__(self, query):

        # Comms sender for querying server. Recvs are done in the
        # main client routine, never here
        self.query = query

        self.song_titles = []
        self._edit_window = None

        # Has username been accepted by server
        self.validated = False

        self.init_gui()

    def init_gui(self):
        super().__init__()
        self.setWindowTitle("PrograBand")

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
        self.validate_btn = QPushButton("Validate Username")
        self.validate_btn.pressed.connect(self.validate_username)
        self.user_text_input.returnPressed.connect(self.validate_btn.pressed)
        user_input.addWidget(self.validate_btn)
        vdiv.addLayout(user_input)

        # 3: Song lists
        song_lists = QHBoxLayout()
        edited = QVBoxLayout()
        ready = QVBoxLayout()

        edited.addWidget(QLabel("Songs being edited"))
        self.edited = QListWidget()
        self.edited.clicked.connect(self.buttons_edit)
        edited.addWidget(self.edited)
        song_lists.addLayout(edited)

        ready.addWidget(QLabel("Songs available"))
        self.ready = QListWidget()
        self.ready.clicked.connect(self.buttons_ready)
        ready.addWidget(self.ready)
        song_lists.addLayout(ready)

        vdiv.addLayout(song_lists)

        # 4: Actions
        actions = QHBoxLayout()
        self.edit_button = QPushButton("Edit")
        self.edit_button.setEnabled(False)
        self.edit_button.pressed.connect(self.edit)
        self.download_button = QPushButton("Download")
        self.download_button.setEnabled(False)
        self.download_button.pressed.connect(self.download)
        actions.addWidget(self.edit_button)
        actions.addWidget(self.download_button)
        vdiv.addLayout(actions)

        # 5: New song
        new_song = QVBoxLayout()
        new_song.addWidget(QLabel("New Song"))
        self.new_song_input = QLineEdit()
        self.new_song_input.textChanged.connect(self.enable_song_create)
        self.new_song_input.setPlaceholderText("Enter name of the new song...")
        new_song.addWidget(self.new_song_input)
        self.new_song_button = QPushButton("Create song")
        self.new_song_button.setEnabled(False)
        self.new_song_button.pressed.connect(self.create_new_song)
        self.new_song_input.returnPressed.connect(self.new_song_button.pressed)
        new_song.addWidget(self.new_song_button)
        vdiv.addLayout(new_song)

        vdiv.setAlignment(Qt.AlignCenter)
        self.setLayout(vdiv)
        self.show()

    def validate_username(self):
        self.query("validate", self.username)

    def username_response(self, resp_dict):
        if not resp_dict['valid']:
            reason = resp_dict['reason']
            msg = QMessageBox()
            msg.setWindowTitle("Error")
            msg.setIcon(QMessageBox.Critical)
            msg.setText("<b>Invalid username</b>")
            msg.setInformativeText(reason)
            msg.exec_()
            return
        else:
            msg = QMessageBox()
            msg.setWindowTitle("Success")
            msg.setText("<b>Success!</b>")
            msg.setInformativeText("You can now edit, download, and create new songs")
            msg.exec_()
        self.user_text_input.setEnabled(False)
        self.validate_btn.setEnabled(False)
        self.validated = True

        self.enable_song_create()

    @property
    def username(self):
        return self.user_text_input.text()

    def enable_song_create(self):
        if not self.validated:
            return
        title = self.new_song_input.text()
        if len(title) < 6 or title in self.song_titles:
           self.new_song_button.setEnabled(False)
        else:
            self.new_song_button.setEnabled(True)

    def buttons_edit(self):
        """
        Updates buttons when focus is on songs being edited
        """
        if not self.validated:
            return
        self.ready.clearSelection()
        self.edit_button.setEnabled(True)
        self.download_button.setEnabled(True)
        self.edit_button.setText("Spectate")

    def buttons_ready(self):
        """
        Updates buttons when focus is on songs not being edited
        """
        if not self.validated:
            return
        self.edited.clearSelection()
        self.edit_button.setText("Edit")
        self.edit_button.setEnabled(True)
        self.download_button.setEnabled(True)

    def edit(self):
        username = self.user_text_input.text()
        title = None
        for field in {self.ready, self.edited}:
            if not field.selectedItems():
                continue
            title = field.selectedItems()[0].data(0)
        if not title:
            raise Exception("What the hell you shouldn't have been"
                            "able to press the button")
        self.query("edit", username, title)

    def download(self):
        title = self.ready.selectedItems()[0].data(0)
        self.query("download", title)

    def create_new_song(self):
        username = self.user_text_input.text()
        title = self.new_song_input.text()
        self.query("create", username, title)

    def update_midis(self, edited_midis, available_midis):
        self.song_titles = edited_midis + available_midis

        self.edited.clear()
        self.ready.clear()
        self.edited.addItems(edited_midis)
        self.ready.addItems(available_midis)

    def load_notes(self, notes):
        if not self._edit_window:
            raise Exception("Client shouldn't have received notes")
        self._edit_window.load_notes(notes)

    def update_connected(self, people):
        if not self._edit_window:
            raise Exception("Client shouldn't have received people")
        self._edit_window.load_people(people)

    def new_messages(self, messages):
        if not self._edit_window:
            raise Exception("Client shouldn't have received messages")
        self._edit_window.load_new_messages(messages)

    def song_menu(self, can_edit):
        self._edit_window = EditingWindow(can_edit, self.username, self.query)
        self._edit_window.closeEvent = self._return_here
        self.hide()

    def _return_here(self, event):
        self.show()
        self.query("finished_editing", self.username)
        super().closeEvent(event)

    def server_crash_notice(self):
        import sys
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText("<b>The server has crashed and the program must close</b>")
        msg.setInformativeText("All your changes are (hopefully) fine")
        sys.exit(msg.exec_())


class EditingWindow(QWidget):
    def __init__(self, is_editor, username, query):
        self.query = query
        self.username = username

        self.init_gui(is_editor)

    def init_gui(self, is_editor):
        super().__init__()
        self.setWindowTitle("Editing Song")
        hdiv = QHBoxLayout()

        # 1: Note editing menu
        # TODO: Make edition more ergonomic
        if is_editor:
            note_menu = QVBoxLayout()

            # a) Pitch
            pitch_layout = QHBoxLayout()
            pitch_layout.addWidget(QLabel("Note"))
            self.pitch = QComboBox()
            notes = ("do - C - 1,do# - C# - 2,re - D - 3,mib - Eb - 4,"
                     "mi - E - 5,fa - F - 6,fa# - F# - 7,sol - G - 8,"
                     "sol# - G# - 9,la - A - 10,sib  - Bb - 11,"
                     "si - B - 12".split(","))
            self.pitch.insertItems(0, notes)
            pitch_layout.addWidget(self.pitch)
            note_menu.addLayout(pitch_layout)

            # b) Scale
            scale_layout = QHBoxLayout()
            self.scale = QSpinBox()
            self.scale.setValue(4)
            self.scale.setRange(0, 10)
            scale_layout.addWidget(QLabel("Scale"))
            scale_layout.addWidget(self.scale)
            note_menu.addLayout(scale_layout)

            # c) Velocity
            vel_layout = QHBoxLayout()
            self.velocity = QComboBox()
            intensities = ("Rest - 0,pppp - 1,ppp - 2,pp - 3,p - 4,mp - 5,"
                           "mf - 6,f - 7,ff - 8,fff - 9,ffff - 10").split(",")
            self.velocity.insertItems(0, intensities)
            self.velocity.setCurrentIndex(5)
            vel_layout.addWidget(QLabel("Note\nVelocity"))
            vel_layout.addWidget(self.velocity)
            note_menu.addLayout(vel_layout)

            # d) Duration
            dur_layout = QHBoxLayout()
            self.duration = QComboBox()
            durations = "4 2 1 1/2 1/4 1/8 1/16".split(" ")
            self.duration.insertItems(0, durations)
            self.duration.setCurrentIndex(4)
            dur_layout.addWidget(QLabel("Note\nLength"))
            dur_layout.addWidget(self.duration)
            note_menu.addLayout(dur_layout)

            # e) Is dotted
            self.is_dotted = QCheckBox("Dotted?")
            note_menu.addWidget(self.is_dotted)

            note_menu.addStretch()

            # f) Buttons
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

        self.chat = QTextEdit()
        self.chat.setReadOnly(True)
        vdiv_chat.addWidget(self.chat)

        type_div = QHBoxLayout()
        self.chat_field = QLineEdit()
        self.chat_field.setPlaceholderText("Type your message here...")
        chat_send = QPushButton("Send")
        chat_send.pressed.connect(self.send_message)
        self.chat_field.returnPressed.connect(chat_send.pressed)
        type_div.addWidget(self.chat_field)
        type_div.addWidget(chat_send)
        vdiv_chat.addLayout(type_div)

        self.connected = QListWidget()
        vdiv_chat.addWidget(self.connected)

        hdiv.addLayout(vdiv_chat)

        # Main layout
        self.setLayout(hdiv)
        self.show()

    def load_notes(self, notes):
        # TODO: SEpARATE BY TRACK
        notes = notes['0']
        self.note_list.clear()
        self.note_list.insertItems(0, notes)
        #self.note_list.scrollToBottom()

    def load_people(self, people):
        self.connected.clear()
        self.connected.insertItems(0, people)
        self.connected.scrollToBottom()

    def load_new_messages(self, messages):
        text = "\n".join(messages)
        self.chat.setText(text)

        # Scroll to bottom
        # https://stackoverflow.com/questions/4939151/how-to-program-scrollbar-to-jump-to-bottom-top-in-case-of-change-in-qplaintexted
        self.chat.verticalScrollBar().setValue(
            self.chat.verticalScrollBar().maximum())

    def add_note(self):
        if not self.note_list.currentRow():
            index = 0
        else:
            index = self.note_list.currentRow()
            
        pitch = self.pitch.currentIndex()
        track = 0
        scale = self.scale.value()
        velocity = self.velocity.currentIndex() - 1
        duration = self.duration.currentIndex() + 1
        dotted = self.is_dotted.isChecked()

        self.query("add_note", self.username, index, track, pitch,
                   scale, velocity, duration, dotted)

    def delete_note(self):
        index = self.note_list.currentRow() - 1
        if not index:
            index = 0
        track = 0
        self.query("delete_note", self.username, index, track)

    def finished(self):
        self.destroyed.emit()

    def send_message(self):
        msg = self.chat_field.text()
        self.chat_field.clear()
        self.query("chat_send", self.username, msg)


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    win = EditingWindow(is_editor=False)
    sys.exit(app.exec_())
