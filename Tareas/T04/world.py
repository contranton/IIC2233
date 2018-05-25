from collections import namedtuple
from misc_lib import Singleton


class World(metaclass=Singleton):
    """
    Container for all 'global' properties.
    """
    def __init__(self):
        self.raining = False
        self.school_day = False
        self.invasion = False
        self.date = (0, 0)


class IWorld(metaclass=Singleton):
    """
    Public interface for the World.
    Allows global parameters to be read, but not changed
    """
    __world = World().__dict__
    __world_namedtuple = namedtuple('WorldParams', __world.keys())

    @property
    def world(self):
        __world_params = self.__world_namedtuple(**self.__world)
        return __world_params

    def __call__(self):
        return self.world
