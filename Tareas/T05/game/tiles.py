from abc import ABCMeta
import numpy as np

import game.parameters as params


class Tile(metaclass=ABCMeta):
    """
    Abstract Object representing a unique tile in a map.  Subclasses
    implement different textures and behaviors for different tiles.
    """

    solid = False
    texture = None
    size = np.array([params.TILE_WIDTH, params.TILE_HEIGHT])

    def __init__(self, position):
        self.position = position


class Ground(Tile):
    texture = "ground.png"


class DestructibleWall(Tile):
    solid = True
    texture = "destructible_wall.png"


class IndestructibleWall(Tile):
    solid = True
    texture = "indestructible_wall.png"
