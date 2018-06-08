import sys
import numpy as np
from collections import defaultdict

from PyQt5.QtWidgets import (QWidget, QApplication, QLabel,
                             QPushButton, QVBoxLayout, QGridLayout,
                             QHBoxLayout, QStackedLayout, QBoxLayout,
                             QGraphicsItem, QGraphicsPixmapItem,
                             QGraphicsScene, QGraphicsView, QGraphicsRectItem)
from PyQt5.QtGui import QPixmap, QDrag, QTransform, QPen

from PyQt5.QtCore import (Qt, QSize, QMimeData, pyqtSignal, QRect,
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
        self.setPixmap(self.sheet.copy(0, 0,
                                       *self.sprite_element_sizes))

        self._update()


    def _update(self):
        if all(self.char_pos() < 0):
            self.setVisible(False)
        else:
            self.setVisible(True)
        self.update_pixmap()
        #print(f"Moving to {self.char_pos()}")
        pos = (self.char_pos()*TILE_SIZE -
               self.sprite_element_sizes*[0.5, 1])
        
        self.setPos(*pos)
        
    def paint(self, painter, *args):
        rect = self.boundingRect()
        painter.setPen(QPen(Qt.red, 1))
        painter.drawRect(rect)
        super().paint(painter, *args)

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
        collision_object = self.character.move(dx, dy)
        if collision_object:
            print(collision_object)
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
        pass

    def place(self, pos):
        self.character.init_position(pos)
        self._update()


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

        self.p1 = QPlayer(Character(self._map.get_solids))
        self.p2 = QPlayer(Character(self._map.get_solids))

        self.addItem(self.p1)
        self.addItem(self.p2)

        self.entities = []


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

        self._keys = defaultdict(lambda: lambda: None)
        self._keys.update({Qt.Key_W:      self._scene.p2.up,
                           Qt.Key_Up:     self._scene.p1.up,
                           Qt.Key_A:      self._scene.p2.left,
                           Qt.Key_Left:   self._scene.p1.left,
                           Qt.Key_D:      self._scene.p2.right,
                           Qt.Key_Right:  self._scene.p1.right,
                           Qt.Key_S:      self._scene.p2.down,
                           Qt.Key_Down:   self._scene.p1.down,
                           Qt.Key_F:      self._scene.p2.lay_bomb,
                           Qt.Key_Space:  self._scene.p1.lay_bomb})

        self._keys_pressed = defaultdict(bool)

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


class MainWindow(QWidget):

    def __init__(self):
        super(MainWindow, self).__init__()
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
        self.show()

        # Event filter to ignore QGraphicsView Arrow key consumption
        self.game_holder.installEventFilter(self)
        #self.installEventFilter(self)

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
           event.key() not in self.game_holder._keys:
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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    sys.exit(app.exec())
