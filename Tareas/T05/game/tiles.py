from PyQt5.QtCore import QObject, pyqtSignal, QTimer

import numpy as np

import parameters as params
from game.entities import Powerup


class TileFacade(QObject):

    id = 1

    def __init__(self, tile_type, position):
        super().__init__()
        self.id = TileFacade.id
        TileFacade.id += 1

        self.position = position
        self.change(tile_type)

    def change(self, tile_type):
        self.tile = tile_type(self.position)
        attrs = {attr: getattr(self.tile, attr) for attr in
                 [i for i in dir(self.tile) if "__" not in i]}
        self.__dict__.update(attrs)

    def __eq__(self, other):
        if isinstance(other, Tile):
            return self.tile == other
        return self.tile == other.tile

    def __repr__(self):
        return f"F{self.tile}"

        
class Tile(QObject):
    """
    Abstract-ish Object representing a unique tile in a map.
    Subclasses implement different textures and behaviors for
    different tiles.

    For convenience we've adopted the Facade pattern. All tiles
    created must be called from the convenience function below and NOT
    this class or the subclasses. This is to allow for dynamic tile
    changes throughout the game.
    """
    
    solid = False
    texture = None
    breakable = False
    size = np.array([params.TILE_SIZE, params.TILE_SIZE])

    collided = pyqtSignal(int)
    exploded_signal = pyqtSignal()

    def __init__(self, position):
        """
        
        """
        super().__init__()

        self.position = position

        # Bool used for damage checking
        self.explosion = False

        self.explosion_timer = QTimer()
        self.explosion_timer.setSingleShot(True)
        self.explosion_timer.timeout.connect(self.end_explode)

    def __repr__(self):
        return f"Tile{self.position}"

    def __eq__(self, other):
        if isinstance(other, TileFacade):
            return self == other.tile
        return super().__cmp__(self, other)
    
    
    @property
    def name(self):
        return self.__class__.name

    def explode(self):
        self.explosion = True
        self.exploded_signal.emit()
        self.explosion_timer.start(params.EXPLOSION_TIME)

    def end_explode(self):
        self.explosion = False


class Ground(Tile):
    solid = False
    breakable = False
    texture = "ground.png"


class DestructibleWall(Tile):
    solid = True
    breakable = True
    texture = "destructible_wall.png"

    def explode(self):
        super().explode()
        return Powerup(self.position, None)


class IndestructibleWall(Tile):
    solid = True
    breakable = False
    texture = "indestructible_wall.png"


_tile_dict = {"0": Ground,
              "P": DestructibleWall,
              "X": IndestructibleWall}

def make_tile(tile_symbol, position):
    return TileFacade(_tile_dict[tile_symbol], position)
