import sys
import os.path as path

from PyQt5.QtWidgets import (QWidget, QApplication, QLabel,
                             QPushButton, QVBoxLayout, QGridLayout,
                             QHBoxLayout, QStackedLayout, QBoxLayout,
                             QGraphicsItem, QGraphicsPixmapItem,
                             QGraphicsScene, QGraphicsView)
from PyQt5.QtGui import QPainter, QPixmap, QDrag

from PyQt5.QtCore import Qt, QSize, QMimeData, pyqtSignal, QRect, QPointF

from parameters import TILE_SIZE
from game.game_map import Map
from game.entities import Character
from game.tiles import Tile


Q_TILE_SIZE = QSize(TILE_SIZE, TILE_SIZE)


class QTile(QGraphicsPixmapItem):
    def __init__(self, tile):
        """
        pass
        """
        super().__init__()
        self.texture = tile.texture
        self.x, self.y = tile.position

        self.setPos(QPointF(self.x, self.y))
        self.setPixmap(QPixmap("assets/{self.texture}"))


class QPlayer(QGraphicsPixmapItem):

    def __init__(self, get_solids_function):
        """
        Graphical player
        """
        super().__init__()
        self.setPixmap(QPixmap("assets/bomberman.png"))
        self.character = Character(get_solids_function)

    def update(self):
        self.setPos(*self.char_pos())
        self.setOffset(10, 10)

    def char_pos(self):
        return (self.character.position*TILE_SIZE)

    def _move(self, dx, dy):
        collision_object = self.character.move(dx, dy)
        if collision_object:
            print(collision_object)
        self.update()

    def up(self):
        self._move(0, -1)

    def right(self):
        self._move(1, 0)

    def down(self):
        self._move(0, 1)

    def left(self):
        self._move(-1, 0)

    def lay_bomb(self):
        pass

    def place(self, pos):
        self.character.init_position(pos)


class QMap(QGraphicsScene):
    def __init__(self, map_):
        """
        """
        super().__init__()
        self._map = map_
        # Graphics Scene to hold tiles and entities
        self.setObjectName("Game self")

        self.tiles = [QTile(tile) for tile in map_.tiles.values()]
        for qtile in self.tiles:
            self.addItem(qtile)

        self.p1 = QPlayer(self._map.get_solids)
        self.p2 = QPlayer(self._map.get_solids)

        self.addItem(self.p1)
        self.addItem(self.p2)

        self.entities = []

    def dragEnterEvent(self, event):
        if event.mimeData().text() == "char":
            event.acceptProposedAction()

    def dropEvent(self, event):
        event.acceptProposedAction()
        # print(f"Player dropped at {event.pos()}")
        pos = event.pos() / TILE_SIZE
        self.p1.place([pos.x(), pos.y()])

    def handleCollision(self, tile):
        print(tile)



class QMapHolder(QWidget):
    def __init__(self, map_):
        """
        DOC
        """
        super().__init__()

        self.setFixedSize(Q_TILE_SIZE*15)
        self._map = map_
        self.scene = QMap(map_)
        self.view = QGraphicsView(self.scene)
        layout = QHBoxLayout()
        layout.addWidget(self.view)
        self.setLayout(layout)
        self.show()


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
        self.game_holder = QMapHolder(Map("mapa.txt"))
        self.game_map = self.game_holder.scene

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

        # Set layours
        layout.addLayout(sublayout)
        self.setLayout(layout)
        self.show()

        # Functions called on key presses
        self._key_map = {Qt.Key_Escape: self.close,
                         Qt.Key_W:      self.game_map.p2.up,
                         Qt.Key_Up:     self.game_map.p1.up,
                         Qt.Key_A:      self.game_map.p2.left,
                         Qt.Key_Left:   self.game_map.p1.left,
                         Qt.Key_D:      self.game_map.p2.right,
                         Qt.Key_Right:  self.game_map.p1.right,
                         Qt.Key_S:      self.game_map.p2.down,
                         Qt.Key_Down:   self.game_map.p1.down,
                         Qt.Key_F:      self.game_map.p2.lay_bomb,
                         Qt.Key_Space:  self.game_map.p1.lay_bomb}

        self._ctrl_key_map = {Qt.Key_P:  self.pause,
                              Qt.Key_E:  self.close}

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
