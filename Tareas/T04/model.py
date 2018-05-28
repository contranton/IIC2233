from collections import deque

from entity import Worker
from misc_lib import Singleton, Logger
from fileio import get_restaurants, get_attractions
from sim import Simulation

from params import (PARK_OPERATORS_AT_GATE, PARK_CLEANERS_PER_RIDE,
                    PARK_TECHS_PER_RIDE, PARK_TOTAL_CAPACITY_FACTOR,
                    PARK_CLOSE_TIME, PARK_OPEN_TIME)


def _counter():
    """
    Generator that yields incremental subsequent values
    """
    i = 0
    while True:
        yield i
        i += 1


class _ClientEntry(object):
    """
    Compacted description of a client used inside Nebiland for
    bookkeeping purposes
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
    queue.
    """
    def _(*args):
        WorkerManager().update_orders()
        result = foo(*args)
        return result
    return _


class Ticket:
    id = 0

    @_manage
    def __init__(self, ride):
        """
        Ticket used for managing requests to clean or fix rides. It must
        be kept by an event callback to periodically check its
        'activated' statem upon which it's understood that the request
        has been processed and is being acted on by the manager.
        """
        Ticket.id += 1
        self.id = Ticket.id
        self.activated = False
        self.worker = None
        self.ride = ride

    def __call__(self):
        """
f        Simplifies checking the state. Returns a bool
        """
        return self.activated

    def activate(self):
        """
        Activate the ticket, signifying that the manager has assigned a
        worker to the task
        """
        self.activated = True

    def assign_worker(self, worker):
        """
        Assign a worker to the ticket
        """
        self.worker = worker
        self.worker.busy = True

    @_manage
    def done(self):
        """
        Called upon completion of the cleaning/fixing task. Frees up
        worker and restores services.
        """
        self.ride.back_in_service()
        self.worker.busy = False


class WorkerManager(metaclass=Singleton):
    """
    Manages the park's workers, giving them orders through a ticket
    system
    """
    def populate(self, num_rides):
        """
        Create workers according to the given number of rides. A sort of
        __init__ I implemented before figuring out there was no issue
        in using them with the singleton pattern xd
        """
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
        """
        Main method for assigning the next task to the next free
        worker. The _manage decorator is used to force this method to
        update and move the simulation forward
        """
        # Assign orders

        if not Nebiland().open:
            return
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
        """
        Return a ticket for the request of type 'type_' on the given
        ride. Ticket must be checked for processing status.
        """
        t = Ticket(ride)
        self.orders[type_].appendleft(t)
        return t

    @property
    def _all_workers(self):
        """
        Returns flattened list of all workers managed. Used to schedule in
        batch.  All praise to
        https://stackoverflow.com/questions/952914/making-a-flat-list-out-of-list-of-lists-in-python
        """
        return [item for sub in [self.operators] +
                list(self.ride_workers.values()) for item in sub]


class Nebiland(metaclass=Singleton):
    """
    State manager for the park.
    """

    restaurants = list(get_restaurants())
    attractions = list(get_attractions())
    Logger().all_rides = attractions
    _clients = {}

    __counter = _counter()

    manager = WorkerManager()
    manager.populate(len(attractions))

    def client_enters(self, name, num_children):
        """
        Registers entry of a client and their children to the park
        """
        # Returns a client id that the client keeps. A sort of ticket.
        c_id = next(self.__counter)
        self._clients[c_id] = \
            _ClientEntry(name=name,
                         children=num_children,
                         entered=Simulation().time,
                         exited=None)
        return c_id

    def client_exits(self, c_id):
        """
        Registers exit of a client and their group
        """
        registry = self._clients[c_id]
        registry.exited = Simulation().time
        registry.in_park = False

    def add_ticket(self, ride, type_):
        """
        Public-ish interface to the manager's ticket creator. Generates a
        ticket for a 'clean' or 'fix' request on 'ride'
        """
        ticket = self.manager.make_job_ticket(ride, type_)
        return ticket

    @property
    def num_rides(self):
        """
        Number of total rides
        """
        return len(self.attractions)

    @property
    def _capacity(self):
        """
        Maximum capacity of the park
        """
        return sum(map(lambda a: a.capacity, self.attractions)) *\
            PARK_TOTAL_CAPACITY_FACTOR

    @property
    def _clients_in_park(self):
        """
        Number of clients currently inside park
        """
        return len(list(filter(lambda c: c.in_park, self._clients.values())))

    def has_capacity(self, group_size):
        """
        Returns True if there's enough space for new_clients in the park
        """
        return self._capacity > self._clients_in_park + group_size

    @property
    def closing_time_today(self):
        return Simulation().time.day_ts() + PARK_CLOSE_TIME.time()

    @property
    def open(self):
        return (PARK_OPEN_TIME.time() <
                Simulation().time.time() <
                PARK_CLOSE_TIME.time())

    def any_valid_restaurants(self, rides_set):
        return len(self.get_valid_restaurants(rides_set)) > 0

    def get_valid_restaurants(self, rides_set):
        rides_set = {r.id for r in rides_set}
        return list(filter(lambda x: x.rides & rides_set, self.restaurants))

    def minimum_budget(self, n_children, rides_set, cant_ride):
        """
        Returns the minimum budget needed to perform any action other than
        resting given the particular set of rides ridden.

        For example, if a client has enough money to go to a
        restaurant but the restaurant requires that they go to a ride
        that's too expensive, the cost associated will be the ride's
        and not the restaurant's
        """
        def tot_cost(costs): return costs[0] + n_children * costs[1]
        budgets = [100000000]
        for restaurant in self.restaurants:
            if not restaurant.rides & rides_set:
                continue
            budgets.append(tot_cost(restaurant.costs))
        for ride in self.attractions:
            if ride in cant_ride:
                continue
            budgets.append(tot_cost(ride.costs))
        return min(budgets)

    @property
    def open_attractions(self):
        return list(filter(lambda a: not a.closed, self.attractions))

    @property
    def attractions_by_queue_length(self):
        return sorted(self.open_attractions,
                      key=lambda a: len(a.queue))


class World(metaclass=Singleton):
    """
    State manager for external events
    """
    school_day = False
    ruziland = False
    raining = False

    def __repr__(self):
        return "World"
