import numpy as np
from PyQt5.QtCore import QObject, pyqtSignal, QTimer

import parameters as params


class Entity(QObject):

    can_clip = False

    def __init__(self, get_solids_function):
        """
        A generic entity that moves in the map.
        """
        super().__init__()

        # Negative position indicates being outside of the map
        self.position = np.array([-1, -1])
        self.velocity = params.SPEED

        # Used for bounding box. Format: width, height.
        # Position is the top-left corner
        self.size = np.array([0.7, 1])

        # Function that returns a map's solid blocks
        self.get_solids = get_solids_function

    def init_position(self, vec2):
        """
        Must receive a positional argument to place the player in the map.
        """
        # TODO: Shift to non solid block
        pos = np.array(vec2).astype(int) + [0.01, 0.01]
        self.position = pos

    def move(self, dx, dy):
        # Negative position means player hasn't been set on map
        if all(self.position < 0):
            return None

        # Calculate new position based on map scale and player velocity
        scale = 1/params.TILE_SIZE
        dpos = np.array([dx, dy]) * scale
        new = self.position + dpos * self.velocity

        # Corners used for rectangular collision checking
        c1, c2 = new + self.size*[0, 0.5], new + self.size
        print(new, c1, c2)
        c1, c2 = tuple(c1.astype(int)), tuple(c2.astype(int))

        if self.can_clip:
            self.position = new
            return None

        # Check for collisions
        # For each corner of our bounding rect
        for c in (c1, c2):
            block = self.get_solids()[c]
            if block:
                return block
        # No collision
        self.position = new
        return None


class Bomb(QTimer, Entity):

    explode_signal = pyqtSignal()

    __num = 0

    def __init__(self, pos, *args):
        super().__init__(*args)
        self.num = Bomb.__num
        Bomb.__num += 1

        self.init_position(pos)
        self.setSingleShot(True)
        self.start(params.EXPLOSION_TIME * 1000)

    def timerEvent(self, *args):
        self.explode_signal.emit()
        self.stop()

    def pushed(self, pusher_pos):
        delta = self.position - pusher_pos
        return delta

    def __repr__(self):
        return f"Bomb{self.num}"


class Character(Entity):

    __num = 1

    place_bomb_signal = pyqtSignal(Bomb)

    def __init__(self, *args):
        """
        Main character class that handles player logic
        """
        super().__init__(*args)

        self.num = self.__num
        Character.__num += 1

        self.lives = params.LIVES
        self.speed = params.SPEED
        self.immune_time = params.IMMUNE_TIME


    def __repr__(self):
        return f"Player(#{self.num}, {self.lives} lives)"

    def __str__(self):
        return f"Player#{self.num}"

    def place_bomb(self):
        bomb = Bomb(self.position, self.get_solids)
        self.place_bomb_signal.emit(bomb)


class Enemy(Entity):
    def __init__(self, *args):
        "docstring"
        super(Enemy, self).__init__(*args)
        self.lives = 1
