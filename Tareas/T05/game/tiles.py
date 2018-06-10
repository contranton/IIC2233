from PyQt5.QtCore import QObject, pyqtSignal

import numpy as np

import parameters as params
from game.entities import Powerup


class Tile(QObject):
    """
    Abstract Object representing a unique tile in a map.  Subclasses
    implement different textures and behaviors for different tiles.
    """

    solid = False
    texture = None
    breakable = False
    size = np.array([params.TILE_SIZE, params.TILE_SIZE])

    collided = pyqtSignal()
    exploded_signal = pyqtSignal()

    def __init__(self, position):
        super().__init__()
        self.position = position

    def __repr__(self):
        return f"Tile{self.position}"

    @property
    def name(self):
        return self.__class__.name

    def explode(self):
        self.exploded_signal.emit()

class Ground(Tile):
    texture = "ground.png"


class DestructibleWall(Tile):
    solid = True
    breakable = True
    texture = "destructible_wall.png"

    def explode(self):
        self.exploded_signal.emit()
        return Powerup(self.position)


class IndestructibleWall(Tile):
    solid = True
    texture = "indestructible_wall.png"

