from collections import namedtuple

from misc_lib import Singleton
from fileio import get_restaurants, get_attractions
from sim import Simulation


def _counter():
    i = 0
    while True:
        yield i
        i += 1


class _ClientEntry(object):
    """
    Documentation for _ClientEntry
    """
    def __init__(self, name, children, entered, exited):
        self.name = name
        self.children = children
        self.entered = entered
        self.exited = exited

        self.in_park = True


class Nebiland(metaclass=Singleton):
    """
    State manager for the park.
    """

    _restaurants = list(get_restaurants())
    _attractions = list(get_attractions())
    _clients = {}

    __counter = _counter()

    def get_valid_restaurants(self, attraction_list):
        pass

    def client_enters(self, name, num_children):
        # Returns a client id that the client keeps. A sort of ticket.
        c_id = next(self.__counter)
        self._clients[c_id] = \
            _ClientEntry(name=name,
                         children=num_children,
                         entered=Simulation().time,
                         exited=None)
        return c_id

    def client_exits(self, c_id):
        registry = self._clients[c_id]
        registry.exited = Simulation().time
        registry.in_park = False

    @property
    def _capacity(self):
        return 1.2 * sum(map(lambda a: a.capacity, self._attractions))

    @property
    def _clients_in_park(self):
        return len(list(filter(lambda c: c.in_park, self._clients.values())))

    @property
    def has_capacity(self):
        return self._capacity > self._clients_in_park

    @property
    def closing_time_today(self):
        return Simulation().time.day * 60 * 24 + 19 * 60


class World(metaclass=Singleton):
    """
    State manager for external events
    """
    school_day = False
