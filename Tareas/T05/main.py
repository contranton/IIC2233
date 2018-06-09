import sys
import numpy as np
from itertools import chain
from collections import defaultdict

from PyQt5.QtWidgets import (QWidget, QApplication, QLabel,
                             QPushButton, QVBoxLayout, QGridLayout,
                             QHBoxLayout, QStackedLayout, QBoxLayout,
                             QGraphicsItem, QGraphicsPixmapItem,
                             QGraphicsScene, QGraphicsView, QGraphicsRectItem)
from PyQt5.QtGui import QPixmap, QDrag, QTransform, QPen

from PyQt5.QtCore import (Qt, QSize, QMimeData, pyqtSignal, QRect, QPoint,
                          QPointF, QObject, QEvent, QTimer)


from parameters import TILE_SIZE
from game.game_map import Map
from game.entities import Character


Q_TILE_SIZE = QSize(TILE_SIZE, TILE_SIZE)


class QTile(QGraphicsPixmapItem):
    def __init__(self, tile):
        """
        pass
        """
        pm = QPixmap(f"assets/{tile.texture}").scaled(Q_TILE_SIZE)
        super().__init__(pm)
        self.tile_type = tile.name

        self.x, self.y = tile.position
        self.setPos(QPointF(self.x, self.y)*TILE_SIZE)


class QPlayer(QGraphicsPixmapItem):

    state_offsets = {"left": (0, 80),
                     "right": (0, 80),
                     "up": (0, 40),
                     "down": (0, 0),
                     "die": (0, 120)}

    sprite_element_sizes = np.array([23, 40])

    def __init__(self, player):
        """
        Graphical player
        """
        self.state = "down"
        self.sheet = QPixmap("assets/bomberman.png")
        self.character = player
        super().__init__()
        self.setPixmap(
            self.sheet.copy(0, 0, *self.sprite_element_sizes)
        )

        self._update()

    @property
    def bounding_size(self):
        return np.array([self.boundingRect().width(),
                         self.boundingRect().height()])

    @property
    def origin(self):
        return self.char_pos()*TILE_SIZE

    def _update(self):
        if all(self.char_pos() < 0):
            self.setVisible(False)
        else:
            self.setVisible(True)
        self.update_pixmap()

        self.setPos(*self.origin)

    def paint(self, painter, *args):
        # Draw pixmap
        super().paint(painter, *args)

        # Draw bounding rectangle
        painter.setPen(QPen(Qt.red, 1))
        painter.drawRect(self.boundingRect())

        # Draw origin
        painter.setPen(QPen(Qt.green, 2))
        painter.drawPoint(self.mapFromScene(*self.char_pos()))

    def update_pixmap(self):
        offs = self.state_offsets[self.state]
        pm = self.sheet.copy(*offs, *self.sprite_element_sizes)\
                       .transformed(QTransform().scale(1.5, 1.5))
        if self.state == "left":
            pm = pm.transformed(QTransform().scale(-1, 1))
        self.setPixmap(pm)

    def char_pos(self):
        return (self.character.position)

    def _move(self, dx, dy):
        self.character.move(dx, dy)
        self._update()

    def up(self):
        self.state = "up"
        self._move(0, -1)

    def right(self):
        self.state = "right"
        self._move(1, 0)

    def down(self):
        self.state = "down"
        self._move(0, 1)

    def left(self):
        self.state = "left"
        self._move(-1, 0)

    def lay_bomb(self):
        self.character.place_bomb()
        return "HII"

    def place(self, pos):
        self.character.init_position(pos)
        self._update()


class QEnemy(QGraphicsPixmapItem):

    def __init__(self):
        super(QEnemy, self).__init__()
        self.sheet = QPixmap("assets/monster.png")
        self.setPixmap(self.sheet.copy(19, 25, 23, 29))


class QBomb(QGraphicsPixmapItem):

    sprite_stages = [(146, 9, 14, 24),
                     (162, 9, 14, 24),
                     (178, 9, 14, 24)]

    def __init__(self, bomb, parent, *args):
        super().__init__(*args)
        self.parent = parent
        self.sheet = QPixmap("assets/bomberman.png")
        self.setPixmap(self.sheet.copy(*self.sprite_stages[0]))
        self.bomb = bomb

        self._update()

    def _update(self):
        self.setPos(*self.bomb.position*TILE_SIZE)

    def explode(self):
        print("Boom")
        self.parent.removeItem(self)


class QMap(QGraphicsScene):
    def __init__(self, view_size, map_):
        """
        """
        super().__init__()

        self._map = map_
        # Graphics Scene to hold tiles and entities
        self.setSceneRect(0, 0, TILE_SIZE, TILE_SIZE)
        self.setObjectName("Game self")

        self.tiles = [QTile(tile) for tile in map_.tiles.values()]
        for qtile in self.tiles:
            self.addItem(qtile)

        self.p1 = QPlayer(self._map.p1)
        self.p2 = QPlayer(self._map.p2)

        self._map.bomb_laid_signal.connect(self.make_bomb)

        self.addItem(self.p1)
        self.addItem(self.p2)

        self.entities = []

    def make_bomb(self, bomb):
        item = QBomb(bomb, parent=self)
        self.addItem(item)
        bomb.explode_signal.connect(item.explode)


class QMapHolder(QGraphicsView):
    def __init__(self, map_):
        """
        DOC
        """
        super().__init__()

        self.setFixedSize(Q_TILE_SIZE*15)
        self._map = map_

        self._scene = QMap(self.rect(), map_)
        self.setScene(self._scene)
        self.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.show()

        # Timer for game time
        self.startTimer(10)

        # Default value is a callable that returns None. These are the
        # 'holdable' keys such as those used for continuous movement
        # motion
        self._keys = defaultdict(lambda: lambda: None)
        self._keys.update({Qt.Key_W:      self._scene.p2.up,
                           Qt.Key_Up:     self._scene.p1.up,
                           Qt.Key_A:      self._scene.p2.left,
                           Qt.Key_Left:   self._scene.p1.left,
                           Qt.Key_D:      self._scene.p2.right,
                           Qt.Key_Right:  self._scene.p1.right,
                           Qt.Key_S:      self._scene.p2.down,
                           Qt.Key_Down:   self._scene.p1.down})

        # These are keys that execute as typical key events do, i.e.,
        # execute once, and start repeating only after a short delay
        self._one_shot_keys = defaultdict(lambda: lambda: None)
        self._one_shot_keys.update({Qt.Key_F:      self._scene.p2.lay_bomb,
                                    Qt.Key_Space:  self._scene.p1.lay_bomb})

        # Utility dict used for managing continuous key events
        self._keys_pressed = defaultdict(bool)

        # Utility set used for the event filter so as to prevent
        # consumption of unused events by this widget
        self.all_keys = {k for k in chain(self._keys.keys(),
                                          self._one_shot_keys.keys())}

    def dragEnterEvent(self, event):
        print("HELLO")
        if event.mimeData().text() == "char":
            event.acceptProposedAction()

    def dropEvent(self, event):
        event.acceptProposedAction()

        pos = event.pos()/TILE_SIZE
        print(f"Player dropped at {pos}")
        self._scene.p1.place([pos.x(), pos.y()])

    def dragMoveEvent(self, event):
        # Must override this to change QGraphicsScene's default
        # drag-and-drop behavior
        event.acceptProposedAction()

    def handleCollision(self, tile):
        print(tile)

    def mousePressEvent(self, event):
        print(self.mapToScene(event.pos()))

    def keyPressEvent(self, event):
        key = event.key()

        # Keys that aren't assosciated with 'continuous' functions
        self._one_shot_keys[key]()

        # Continuously active functions
        if key in self._keys:
            self._keys_pressed[key] = True

    def keyReleaseEvent(self, event):
        key = event.key()
        if self._keys_pressed[key]:
            self._keys_pressed[key] = False

    def timerEvent(self, event):
        keys = (k for (k, p) in self._keys_pressed.items() if p)
        for k in keys:
            self._keys[k]()


class QDraggableChar(QWidget):
    def __init__(self):
        """
        """
        super().__init__()
        layout = QHBoxLayout()
        layout.setObjectName("Draggable char holder")
        layout.addWidget(QLabel("DRAG ME"))
        self.setLayout(layout)

    def mousePressEvent(self, event):
        # Tips from http://doc.qt.io/qt-5/dnd.html

        if(event.button() == Qt.LeftButton):
            print("Draggin")
            data = QMimeData()
            data.setText("char")

            drag = QDrag(self)
            drag.setMimeData(data)
            drag.setPixmap(QPixmap("assets/nukeman.png"))
            drag.exec()


class GameWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("C o d e   W i t h   F i r e")
        self.setObjectName("Main window")

        # Game window
        self.game_holder = QMapHolder(Map("mapa.txt"))
        self.game_map = self.game_holder.scene()

        # Main horizontal layout
        layout = QHBoxLayout(self)
        layout.setObjectName("Horizontal div")
        layout.addWidget(self.game_holder)

        # Vertical sublayout
        sublayout = QVBoxLayout(self)
        sublayout.setObjectName("Right vertical div")
        sublayout.addStretch()
        sublayout.addWidget(QLabel("WELCOME TO <i><b>NOT</b></i>&nbsp;"
                                   " BOMBERMAN!"))
        sublayout.addStretch()
        sublayout.addWidget(QDraggableChar())
        sublayout.addStretch()

        # Set layouts
        layout.addLayout(sublayout)
        self.setLayout(layout)

        # Event filter to ignore QGraphicsView Arrow key consumption
        self.game_holder.installEventFilter(self)

        # Functions called on key presses
        self._key_map = {Qt.Key_Escape: self.close}
        self._ctrl_key_map = {Qt.Key_P:  self.pause,
                              Qt.Key_E:  self.close}

    def eventFilter(self, source, event):
        """
        Event Filter used to prevent consumption of arrow keys by the
        QGraphicsView.

        Adapted from
        http://www.qtcentre.org/threads/25487-Detect-Arrow-Keys
        """
        if event.type() == QEvent.KeyPress and\
           event.key() not in self.game_holder.all_keys:
            self.keyPressEvent(event)
            return True
        else:
            return super().eventFilter(self, event)

    def keyPressEvent(self, event):
        key_dict = self._key_map

        # Check if CTRL is pressed
        if QApplication.keyboardModifiers() == Qt.ControlModifier:
            key_dict = self._ctrl_key_map

        # Attempt to find and run asssociated callback function
        try:
            callback = key_dict[event.key()]
            callback()
        except KeyError:
            # Faster to catch this error rather than checking through
            # all callbacks at every input event
            pass

    def pause(self):
        pass

class MainWindow(QWidget):

    def __init__(self):
        """
    
        """
        super().__init__()

        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("<b>Welcome to CODE WITH FIRE</b>"))
        bt1 = QPushButton("Single Player")
        bt2 = QPushButton("Two Players")
        bt3 = QPushButton("Scores")
        bt4 = QPushButton("Exit")
        bt1.pressed.connect(self.play_single)
        bt2.pressed.connect(self.play_double)
        bt3.pressed.connect(self.scores_menu)
        bt4.pressed.connect(self.close)
        layout.addWidget(bt1)
        layout.addWidget(bt2)
        layout.addWidget(bt3)
        layout.addWidget(bt4)

        self.setLayout(layout)
        self.show()

    def scores_menu(self):
        pass

    def play_single(self):
        self.hide()
        GameWindow().show()

    def play_double(self):
        self.hide()
        GameWindow().show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    sys.exit(app.exec())
