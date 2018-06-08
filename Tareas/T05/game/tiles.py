from abc import ABCMeta
import numpy as np

import parameters as params


class Tile(metaclass=ABCMeta):
    """
    Abstract Object representing a unique tile in a map.  Subclasses
    implement different textures and behaviors for different tiles.
    """

    solid = False
    texture = None
    size = np.array([params.TILE_SIZE, params.TILE_SIZE])

    def __init__(self, position):
        self.position = position

    def __repr__(self):
        return f"Tile{self.position}"

    @property
    def name(self):
        return self.__class__.name

    def collide(self, x, y):
        if any(0 < np.array([x, y]) - self.position < np.array([1, 1])):
            print(f"Collided with {self}")
            return True
        return False


class Ground(Tile):
    texture = "ground.png"


class DestructibleWall(Tile):
    solid = True
    texture = "destructible_wall.png"


class IndestructibleWall(Tile):
    solid = True
    texture = "indestructible_wall.png"
