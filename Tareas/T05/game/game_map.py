import numpy as np

from game.tiles import (Ground, DestructibleWall,
                        IndestructibleWall)


class Map:

    _tile_dict = {"0": Ground,
                  "P": DestructibleWall,
                  "X": IndestructibleWall}

    def __init__(self, map_path):
        """
        Holder for all tiles with their coordinates

        Coordinates are 0-indexed, and origin is at the top-left of
        the map.txt file.
        """

        # Dictionary position: Tile
        self.tiles = {}

        # Loads map from file
        self.load_map(map_path)

    def load_map(self, map_path):
        """
        Reads map file and creates appropiate tile objects
        """

        # Read file
        map_str = []
        with open(map_path, 'r') as f:
            for row in f.readlines():
                map_str.append(row.strip().split(" "))

        # Create Tiles with map position as key
        for i, row in enumerate(map_str):
            for j, tile_str in enumerate(row):
                pos = (i, j)

                tile_class = self._tile_dict[tile_str]
                self.tiles[pos] = tile_class(pos)
 
    def get_solids(self):
        return {k: v for k, v in self.tiles.items() if v.solid}

