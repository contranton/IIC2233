"""
Backend wrappers for GUI
"""

import sys

from abc import ABCMeta
from PyQt5.QtWidgets import (QWidget, QApplication, QObject, QOpenGLWidget)

from params import TILE_WIDTH, TILE_HEIGHT


class QTile(QWidget):
    """
    QWidget representation of a Tile
    """

    solid = True
    texture = None

    def __init__(self, tile):
        """
        Define widgety behavior yo
        """
        super().__init__()
        self._tile = tile

        # TODO: Map position to proper pixel coordinates
        self.setGeometry(*self.tile.position, TILE_WIDTH, TILE_HEIGHT)
        self.show()




class QCharacter(QObject):
    def __init__(self, char):
        self.char = char


    
class QMap(QWidget):
    def __init__(self, map):
        """

        """
        self._map = map
        
