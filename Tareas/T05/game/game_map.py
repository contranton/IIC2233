from PyQt5.QtCore import QObject, pyqtSignal

from game.tiles import (Ground, DestructibleWall,
                        IndestructibleWall)
from game.entities import Character, Bomb


class Map(QObject):

    _tile_dict = {"0": Ground,
                  "P": DestructibleWall,
                  "X": IndestructibleWall}

    bomb_laid_signal = pyqtSignal(Bomb)
    
    def __init__(self, map_path):
        """
        Holder for all tiles with their coordinates

        Coordinates are 0-indexed, and origin is at the top-left of
        the map.txt file.
        """
        super().__init__()

        # Dictionary of the form:
        # position(i, j): Tile
        self.tiles = {}
        self.solids = {}

        # Loads map from file
        self.load_map(map_path)

        # True if a block has changed. Initially true on creation to
        # allow setting of solid blocks
        self.changed = True

        # Players contained in map
        self.p1 = Character(self.get_solids)
        self.p2 = Character(self.get_solids)

        self.p1.place_bomb_signal.connect(self.place_bomb)
        self.p2.place_bomb_signal.connect(self.place_bomb)

        self.active_bombs = []

    def load_map(self, map_path):
        """
        Reads map file and creates appropiate tile objects
        """

        # Read file
        map_str = []
        with open(map_path, 'r') as file:
            for row in file.readlines():
                map_str.append(row.strip().split(" "))

        # Create Tiles with map position as key
        for i, row in enumerate(map_str):
            for j, tile_str in enumerate(row):
                pos = (i, j)

                tile_class = self._tile_dict[tile_str]
                self.tiles[pos] = tile_class(pos)

    def get_solids(self):
        if self.changed:
            self.solids = {k: (v if v.solid else None)
                           for k, v in self.tiles.items()}
            self.changed = False
        return self.solids

    def place_bomb(self, bomb):
        if len(self.active_bombs) >= 1:
            return

        bomb.explode_signal.connect(self.bomb_explode)
        self.active_bombs.append(bomb)
        self.bomb_laid_signal.emit(bomb)

    def bomb_explode(self):
        bomb = self.sender()
        self.active_bombs.remove(bomb)
