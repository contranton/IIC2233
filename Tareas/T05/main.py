import sys
import numpy as np
from itertools import chain
from collections import defaultdict

from PyQt5.QtWidgets import (QWidget, QApplication, QLabel,
                             QPushButton, QVBoxLayout, QHBoxLayout,
                             QGraphicsPixmapItem, QGraphicsScene,
                             QGraphicsView, QTextEdit)
from PyQt5.QtGui import QPixmap, QDrag, QTransform, QPen, QColor

from PyQt5.QtCore import (Qt, QSize, QMimeData, pyqtSignal, QRectF,
                          QPointF, QEvent, QTimer, QPoint)


from parameters import TILE_SIZE, ANIM_SPEED, TICK_RATE, EXPLOSION_TIME, LIVES
from game.game_map import Map


Q_TILE_SIZE = QSize(TILE_SIZE, TILE_SIZE)


class QTile(QGraphicsPixmapItem):

    explosion_texture = "assets/boom.png"
    explosion_frames = [(128*j, 128*i, 128, 128) for i in range(8)
                        for j in range(8)]

    def __init__(self, tile):
        """
        pass
        """
        super().__init__()
        self.tile = tile
        self.tile.exploded_signal.connect(self.explode)
        self.update_pixmap()

        self.x, self.y = tile.position
        self.setPos(QPointF(self.x, self.y)*TILE_SIZE)

        # For explosion animation
        self.expl_sheet = QPixmap(self.explosion_texture)
        self.exploded = False
        self.num_frames = len(self.explosion_frames)

        self.frame = 0
        self.anim_timer = QTimer()
        self.anim_timer.timeout.connect(self.increase_frame)

    def update_pixmap(self):
        pm = QPixmap(f"assets/{self.tile.texture}").scaled(Q_TILE_SIZE)
        self.setPixmap(pm)

    def paint(self, painter, *args):
        super().paint(painter, *args)
        if self.exploded:
            boom = self.expl_sheet.copy(*self.explosion_frames[self.frame])
            #boom = boom.transformed(QTransform().scale(5, 5))
            painter.fillRect(0, 0, TILE_SIZE, TILE_SIZE, QColor(128, 0, 0, 128))
            painter.drawPixmap(0, 0, TILE_SIZE, TILE_SIZE, boom)

    def explode(self):
        self.exploded = True
        print("Updating tile {tile}")
        self.update_pixmap()
        self.frame = 0
        self.anim_timer.start(1000*EXPLOSION_TIME/self.num_frames)

    def increase_frame(self):
        self.update()
        if self.frame >= self.num_frames - 1:
            self.exploded = False
            self.anim_timer.stop()
        else:
            self.frame += 1


class QEntity(QGraphicsPixmapItem):

    # Dictionary that contains the list of rectangles inside the
    # spritesheet that correspond to different frames of a single
    # state
    state_offsets = {"default": [(0, 0, 1, 1)]}

    flipped = ["left"]

    # Path to the image file
    texture = ""

    def __init__(self, entity, parent=None):
        super().__init__()
        self.parent = parent

        self.entity = entity
        self.sheet = QPixmap(self.texture)
        self.state = "default"

        self.opacity = 1

        self.frame = 0
        self.tickTimer = QTimer()
        self.tickTimer.start(TICK_RATE)
        self.tickTimer.timeout.connect(self.tickTimerEvent)

        self.animTimer = QTimer()
        self.animTimer.start(1000/ANIM_SPEED)
        self.animTimer.timeout.connect(self.animTimerEvent)

        #self.update_pixmap()

    def animTimerEvent(self):
        self.frame += 1

    def tickTimerEvent(self):
        pass
    
    def boundingRect(self):
        return QRectF(0, 0, TILE_SIZE, TILE_SIZE)

    @property
    def pos(self):
        return self.entity.position

    @property
    def bounding_size(self):
        return np.array([self.boundingRect().width(),
                         self.boundingRect().height()])

    @property
    def origin(self):
        return self.pos*TILE_SIZE - self.bounding_size/2

    def paint(self, painter, *args):
        # Draw pixmap
        # TODO: Fix sprite falling out of the bounding box
        painter.setOpacity(self.opacity)
        super().paint(painter, *args)

        # Draw bounding rectangle
        #painter.setPen(QPen(Qt.red, 1))
        #painter.drawRect(self.boundingRect())

        # Draw origin
        #painter.setPen(QPen(Qt.green, 2))
        #painter.drawPoint(self.mapFromScene(*self.pos))

    def update_pixmap(self):
        # Tuple containing coordinates for each state animation
        subsheet = self.state_offsets[self.state]
        offs = subsheet[self.frame % len(subsheet)]

        # Get pixmap from aquired coordinate
        sprite_size = TILE_SIZE * self.entity.size
        pm = self.sheet.copy(*offs).scaled(*sprite_size)

        # Reflect the left state
        if self.state == "left":
            pm = pm.transformed(QTransform().scale(-1, 1))

        # Assign
        self.setPixmap(pm)
        self.setOffset(*sprite_size*[0.5, 0])


class QPlayer(QEntity):

    state_offsets = {"left":  [(6 + 21*i, 84, 20, 31) for i in range(5)],
                     "right": [(6 + 21*i, 84, 20, 31) for i in range(5)],
                     "up":    [(7 + 21*i, 47, 16, 28) for i in range(5)],
                     "down":  [(7 + 21*i,  4, 16, 32) for i in range(5)],
                     "die":   [(5 + 29*i, 120, 24, 40) for i in range(7)],
                     "default": [(49, 8, 18, 32)]}

    texture = "assets/bomberman.png"

    def __init__(self, *args):
        super().__init__(*args)
        self._update()
        self.entity.invincible_signal.connect(self.invincible)

    def _update(self):
        if all(self.pos < 0):
            self.setVisible(False)
        else:
            self.setVisible(True)
        self.update_pixmap()

        self.setPos(*self.origin)

    def _move(self, dx, dy):
        self.entity.move(dx, dy)
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

    def invincible(self, is_set):
        if is_set:
            self.opacity = 0.25
        else:
            self.opacity = 1
        super().update()

    def lay_bomb(self):
        self.entity.place_bomb()
        return "HII"

    def place(self, pos):
        self.entity.init_position(pos)
        self._update()


class QEnemy(QEntity):

    state_offsets = {"default": [(19, 25, 23, 29)]}
    texture = "assets/monster.png"

    def tickTimerEvent(self):
        super().tickTimerEvent()
        self.entity.auto_move()
        self.update_pixmap()
        self.setPos(*self.origin)

    def delete(self):
        self.parent.removeItem(self)


class QBomb(QGraphicsPixmapItem):

    sprite_stages = [(146, 9, 14, 24),
                     (162, 9, 14, 24),
                     (178, 9, 14, 24)]

    def __init__(self, bomb, parent, *args):
        super().__init__(*args)
        self.parent = parent
        self.sheet = QPixmap("assets/bomberman.png")
        self.bomb = bomb

        self.timer = QTimer()
        self.timer.start(TICK_RATE)
        self.timer.timeout.connect(self.timerEvent)

    def timerEvent(self):
        pm = self.sheet.copy(*self.sprite_stages[0])
        pm = pm.transformed(QTransform().scale(2, 2))
        self.setPixmap(pm)
        self.bomb.update()
        self.setPos(*self.bomb.position*TILE_SIZE)

    def delete(self):
        self.parent.removeItem(self)

class QPowerup(QGraphicsPixmapItem):

    def __init__(self, powerup, parent):
        """

        """
        super().__init__()
        self.parent = parent
        self.powerup = powerup
        self.sheet = QPixmap(f"assets/{powerup.powerup_type}.png")\
                             .scaled(Q_TILE_SIZE)
        self.setPixmap(self.sheet)
        self.setPos(*self.powerup.position*TILE_SIZE)


    def delete(self):
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
        self._map.new_enemy_signal.connect(self.make_enemy)
        self._map.powerup_placed_signal.connect(self.make_powerup)

        self.addItem(self.p1)
        self.addItem(self.p2)

        self.entities = []

    def make_bomb(self, bomb):
        item = QBomb(bomb, parent=self)
        self.addItem(item)
        bomb.explode_signal.connect(item.delete)

    def make_enemy(self, enemy):
        item = QEnemy(enemy, parent=self)
        self.addItem(item)
        enemy.dead.connect(item.delete)

    def make_powerup(self, powerup):
        item = QPowerup(powerup, parent=self)
        self.addItem(item)
        powerup.taken.connect(item.delete)


class QHeart(QLabel):
    def __init__(self, num):
        super(QHeart, self).__init__()
        self.num = num
        self.sheet = QPixmap("assets/life_hearts.png")
        self.size = 200/LIVES
        self.setFixedSize(self.size, self.size)
        self.setText("A heart")
        self.alive()

    def alive(self):
        self.setPixmap(self.sheet.copy(0, 0, 50, 50)
                       .scaled(self.size, self.size))

    def dead(self):
        self.setPixmap(self.sheet.copy(50, 0, 50, 50)
                       .scaled(self.size, self.size))

    def update(self, num):
        if self.num < num:
            self.alive()
        else:
            self.dead()

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
        self.startTimer(TICK_RATE)

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
        if event.mimeData().text() in "12":
            event.acceptProposedAction()

    def dropEvent(self, event):
        event.acceptProposedAction()

        pos = event.pos()/TILE_SIZE
        
        if self._map.tiles[(pos.x(), pos.y())].solid:
            return
        print(f"Player dropped at {pos}")
        player = {"1": self._scene.p1, "2": self._scene.p2}
        player[event.mimeData().text()].place([pos.x(), pos.y()])

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
    def __init__(self, num):
        """
        """
        super().__init__()
        layout = QHBoxLayout()
        layout.setObjectName("Draggable char holder")
        layout.addWidget(QLabel("DRAG ME"))
        self.setLayout(layout)

        self.num = num

    def mousePressEvent(self, event):
        # Tips from http://doc.qt.io/qt-5/dnd.html

        if(event.button() == Qt.LeftButton):
            print("Draggin")
            data = QMimeData()
            data.setText(f"{self.num}")

            drag = QDrag(self)
            drag.setMimeData(data)
            pixmap = QPixmap("assets/bomberman3d.png")\
                     .transformed(QTransform().scale(-0.15, 0.15))
            drag.setPixmap(pixmap)
            drag.setHotSpot(QPoint(self.width()/4, self.height()))
            drag.exec()


class QLives(QWidget):

    update_signal = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.layout = QHBoxLayout()
        for i in range(LIVES):
            heart = QHeart(i)
            self.update_signal.connect(heart.update)
            self.layout.addWidget(heart)
        self.setFixedWidth(200)
        self.setLayout(self.layout)

    def update_lives(self, num):
        self.update_signal.emit(num)


class QScore(QLabel):
    def __init__(self, name):
        self.template = f"<b>{name}'s score:</b> "
        super().__init__(self.template)
        self.update_score(0)

    def update_score(self, num):
        self.setText(f"{self.template} {num}")


class QPlayerInfo(QWidget):

    def __init__(self, player):
        super().__init__()

        layout = QVBoxLayout(self)
        lives = QLives()
        player.lives_changed.connect(lives.update_lives)
        layout.addWidget(lives)
        label = QScore(player)
        player.score_changed.connect(label.update_score)
        layout.addWidget(label)
        layout.addWidget(QDraggableChar(player.num))

        self.setLayout(layout)


class GameWindow(QWidget):

    closed_signal = pyqtSignal()

    def __init__(self, multiplayer, names):
        super().__init__()
        self.setWindowTitle("C o d e   W i t h   F i r e")
        self.setObjectName("Main window")

        # Game window
        self.game_holder = QMapHolder(Map("mapa.txt", names))
        self.game_map = self.game_holder.scene()

        # Main horizontal layout
        layout = QHBoxLayout(self)
        layout.setObjectName("Horizontal div")
        layout.addWidget(self.game_holder)

        sublayout = QVBoxLayout(self)
        sublayout.addStretch()
        sublayout.addWidget(QPlayerInfo(self.game_map._map.p1))
        if multiplayer:
            sublayout.addStretch()
            sublayout.addWidget(QPlayerInfo(self.game_map._map.p2))
        sublayout.addStretch()

        # Set layouts
        layout.addLayout(sublayout)
        self.setLayout(layout)

        # Event filter to ignore QGraphicsView Arrow key conansumption
        self.game_holder.installEventFilter(self)

        # Functions called on key presses
        self._key_map = {Qt.Key_Escape: self.close}
        self._ctrl_key_map = {Qt.Key_P:  self.pause,
                              Qt.Key_E:  self.close}

        self.show()

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

    def close(self):
        self.closed_signal.emit()
        super().close()


class QNameWindow(QWidget):
    def __init__(self, refocus_foo, multiplayer=False):
        """

        """
        super().__init__()
        self.mult = multiplayer
        self.refocus_foo = refocus_foo

        self.text_fields = [QTextEdit(f"Player{i+1}") for i in range(2)]

        vdiv = QVBoxLayout()
        hdiv = QHBoxLayout()
        for i in range(1 + 1*multiplayer):
            print(i)
            subvdiv = QVBoxLayout()
            subvdiv.addWidget(QLabel(f"Name of player {i}"))
            subvdiv.addWidget(self.text_fields[i])
            hdiv.addLayout(subvdiv)
        vdiv.addLayout(hdiv)
        self.btn = QPushButton("Start Game")
        self.btn.pressed.connect(self.on_press)
        vdiv.addWidget(self.btn)

        self.setLayout(vdiv)

        self.show()

    def on_press(self):
        self.hide()
        names = [t.toPlainText() for t in self.text_fields]
        self.game = GameWindow(self.mult, names)
        self.game.closed_signal.connect(self.refocus_foo)


class MainWindow(QWidget):

    def __init__(self):
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
        self.name_window = QNameWindow(self.refocus, multiplayer=False)

    def play_double(self):
        self.hide()
        self.name_window = QNameWindow(self.refocus, multiplayer=True)

    def refocus(self):
        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    #win = MainWindow()
    win = GameWindow(False, ["Player1", ""])
    sys.exit(app.exec())
