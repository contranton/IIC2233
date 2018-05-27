from copy import deepcopy
from collections import deque

from entity import Worker
from misc_lib import Singleton, Logger
from fileio import get_restaurants, get_attractions
from sim import Simulation

from params import (PARK_OPERATORS_AT_GATE, PARK_CLEANERS_PER_RIDE,
                    PARK_TECHS_PER_RIDE, PARK_TOTAL_CAPACITY_FACTOR,
                    PARK_CLOSE_TIME)


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


def _manage(foo):
    """
    Decorator for methods in WorkerManager or Ticket which trigger a
    system update, i.e. sending off workers and updating the order
    queue
    """
    def _(*args):
        WorkerManager().update_orders()
        result = foo(*args)
        return result
    return _


class Ticket:
    id = 0

    def __init__(self, ride):
        Ticket.id += 1
        self.id = Ticket.id
        self.activated = False
        self.worker = None
        self.ride = ride

    def __call__(self):
        if self.activated:
            print("TICKET %i ACTIVATED" % self.id)
            #self.activated = False
            return True
        return False

    def activate(self):
        self.activated = True
        self.ride.out_of_service()

    def assign_worker(self, worker):
        self.worker = worker
        self.worker.busy = True

    @_manage
    def done(self):
        self.ride.back_in_service()
        self.worker.busy = False


class WorkerManager(metaclass=Singleton):

    def populate(self, num_rides):
        self.operators = [Worker()
                          for i in range(num_rides + PARK_OPERATORS_AT_GATE)]
        self.ride_workers = {
            "clean": [Worker()
                      for i in range(num_rides // PARK_CLEANERS_PER_RIDE)],
            "fix": [Worker()
                    for i in range(num_rides // PARK_TECHS_PER_RIDE)]
        }

        self.orders = {
            "clean": deque(),
            "fix": deque()
        }

    def update_orders(self):
        # Assign orders

        for worker_type, order_queue in self.orders.items():
            if order_queue:
                worker = next(filter(lambda f: not f.busy,
                                     self.ride_workers[worker_type]),
                              None)
                if worker:
                    ticket = order_queue.pop()
                    ticket.activate()
                    ticket.assign_worker(worker)

    @_manage
    def make_job_ticket(self, ride, type_):
        t = Ticket(ride)
        self.orders[type_].appendleft(t)
        return t

    @property
    def _all_workers(self):
        return [self.operators] + [*list(self.ride_workers.values())]


class Nebiland(metaclass=Singleton):
    """
    State manager for the park.
    """

    restaurants = list(get_restaurants())
    attractions = list(get_attractions())
    Logger().all_rides = deepcopy(attractions)
    _clients = {}

    __counter = _counter()

    manager = WorkerManager()
    manager.populate(len(attractions))

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

    def add_ticket(self, ride, type_):
        ticket = self.manager.make_job_ticket(ride, type_)
        return ticket

    @property
    def num_rides(self):
        return len(self.attractions)

    @property
    def _capacity(self):
        return sum(map(lambda a: a.capacity, self.attractions)) *\
            PARK_TOTAL_CAPACITY_FACTOR

    @property
    def _clients_in_park(self):
        return len(list(filter(lambda c: c.in_park, self._clients.values())))

    @property
    def has_capacity(self):
        return self._capacity > self._clients_in_park

    @property
    def closing_time_today(self):
        return Simulation().time.day * 60 * 24 + PARK_CLOSE_TIME[0] * 60\
            + PARK_CLOSE_TIME[1]

    def any_valid_restaurants(self, rides_set):
        return len(self.get_valid_restaurants(rides_set)) > 0

    def get_valid_restaurants(self, rides_set):
        return list(filter(lambda x: x.rides & rides_set, self.restaurants))

    @property
    def open_attractions(self):
        return list(filter(lambda a: not a.closed, self.attractions))

    @property
    def attractions_by_queue_length(self):
        return sorted(deepcopy(self.open_attractions),
                      key=lambda a: len(a.queue))


class World(metaclass=Singleton):
    """
    State manager for external events
    """
    school_day = False
    ruziland = False
