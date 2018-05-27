from random import normalvariate, expovariate, uniform, random
from collections import deque

from faker import Faker

from fileio import get_associations
from sim import Simulation

# The M-q keybinding is the best hngggg
from params import (CLIENT_PATIENCE_MU_OFFSET,
                    CLIENT_PATIENCE_MU_SLOPE, CLIENT_PATIENCE_SIGMA,
                    CLIENT_VOMIT_THRESHOLD, CLIENT_VOMIT_CHANCE,
                    CLIENT_VOMIT_SETTLE, CLIENT_BREAK_ENERGY,
                    CLIENT_NAUSEA_MAX, CLIENT_HEIGHT_ADULT_MU,
                    CLIENT_HEIGHT_ADULT_SIGMA, CLIENT_HEIGHT_CHILD_MU,
                    CLIENT_HEIGHT_CHILD_SIGMA,
                    CLIENT_HUNGER_INITIAL_LOWER,
                    CLIENT_HUNGER_INITIAL_UPPER,
                    RUZILAND_FAILURE_RATE_FACTOR,
                    RIDE_MAX_CLEANING_TIME, RESTAURANT_ADULT_PREP,
                    RESTAURANT_CHILD_PREP)

fkr = Faker()


class Entity:
    # world = property(lambda _: IWorld().world)

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, self.name)


class Client(Entity):
    def __init__(self):
        self.name = fkr.name()
        self._energy = 1
        self._hunger = uniform(CLIENT_HUNGER_INITIAL_LOWER,
                               CLIENT_HUNGER_INITIAL_UPPER)
        self._nausea = 0
        self._budget = 0

        self._height = normalvariate(CLIENT_HEIGHT_ADULT_MU,
                                     CLIENT_HEIGHT_ADULT_SIGMA)
        self._children = []

        self.rides_ridden = set()

        self.cant_ride_list = []
        self.client_id = None
        self.has_left = False
        self.got_on = False
        self.willing_to_queue = True

    def add_child(self, child):
        child.adult = self
        self._children.append(child)

    @property
    def num_throw_up(self):
        num = 0
        for p in [self] + [c for c in self._children]:
            if p.nausea > CLIENT_VOMIT_THRESHOLD and\
               random() < CLIENT_VOMIT_CHANCE:
                num += 1
                p.nausea = CLIENT_VOMIT_SETTLE
        return num

    @property
    def children(self):
        return [c.name for c in self._children]

    @property
    def patience(self):
        return int(normalvariate(
            CLIENT_PATIENCE_MU_OFFSET +
            CLIENT_PATIENCE_MU_SLOPE*self._energy,
            CLIENT_PATIENCE_SIGMA))

    @property
    def budget(self):
        return self._budget

    @budget.setter
    def budget(self, value):
        self._budget = value

    @property
    def num_children(self):
        return len(self._children)

    @property
    def _all_energies(self):
        return [self._energy] + [c._energy for c in self._children]

    @property
    def _all_hungers(self):
        return [self._hunger] + [c._hunger for c in self._children]

    @property
    def _all_heights(self):
        return [self._height] + [c._height for c in self._children]
    
    def any_height_below(self, height):
        return any(map(lambda x: x < height, self._all_heights))

    @property
    def minimum_energy(self):
        return min(self._all_energies)

    def any_energy_less_than(self, value):
        return any(map(lambda x: x < value, self._all_energies))

    @property
    def average_hunger(self):
        return sum(self._all_hungers) / (self.num_children + 1)

    def rest(self):
        self._energy = min(self._energy + CLIENT_BREAK_ENERGY, 1)
        for c in self._children:
            c._energy = min(c._energy + CLIENT_BREAK_ENERGY, 1)

    @property
    def nausea(self):
        return self._nausea

    @nausea.setter
    def nausea(self, value):
        self._nausea = min(max(value, 0), CLIENT_NAUSEA_MAX)

    @property
    def hunger(self):
        return self._hunger

    @hunger.setter
    def hunger(self, value):
        self._hunger = min(max(value, 0), 1)

    def increase_children_nausea(self, value):
        for c in self._children:
            c._nausea = min(c._nausea + value, CLIENT_NAUSEA_MAX)

    def reduce_all_hungers(self, value):
        self.hunger -= value
        for c in self._children:
            c._hunger = max(c._hunger - value, 0)


class Child(Entity):
    def __init__(self):
        self.name = fkr.name()
        self._energy = 1
        self._hunger = uniform(CLIENT_HUNGER_INITIAL_LOWER,
                               CLIENT_HUNGER_INITIAL_UPPER)
        self._nausea = 0
        self._budget = 0

        self._height = normalvariate(CLIENT_HEIGHT_CHILD_MU,
                                     CLIENT_HEIGHT_CHILD_SIGMA)
        self.adult = None


class Worker(Entity):
    def __init__(self):
        self.name = fkr.name()
        self.busy = False

    def __repr__(self):
        s = "BUSY" if self.busy else ""
        return s

class Attraction(Entity):
    def __init__(self, id, name, type_, adult_cost, child_cost, capacity,
                 duration, min_height, dirt_limit, max_time):
        self.id = int(id)
        self.name = name
        self.type = type_
        self.adult_cost = int(adult_cost)
        self.child_cost = int(child_cost)
        self.capacity = int(capacity)
        self.duration = int(duration)
        self.min_height = int(min_height)
        self.dirt_limit = int(dirt_limit)
        self.max_time = int(max_time)
        self._dirt = 0

        self.queue = deque()

        self.closed = False
        self._time_begin_oos = 0

        self.time_with_at_least_one_person = None

    def __repr__(self):
        return "Ride({}:{})".format(self.id, self.name)

    def add_to_queue(self, client):
        if len(self.queue) == 0:
            self.time_with_at_least_one_person = Simulation().time.raw()
        self.queue.appendleft(client)

    def remove_from_queue(self, client):
        self.queue.remove(client)

    def start(self):
        from events.client_events import callback_enter_ride
        from events.park_events import operator_check_ride
        if not operator_check_ride(self):
            # Ride must be serviced and can't be ridden right now
            return

        cap = self.capacity
        riders = [self.queue.pop()
                  for i in range(min(cap, len(self.queue)))]
        [callback_enter_ride(rider) for rider in riders]

        self.time_with_at_least_one_person = 0

    def can_begin(self):
        if self.closed:
            return False
        t = self.time_with_at_least_one_person
        if t is not None and (Simulation().time.raw() - t) > self.max_time:
            return True
        else:
            return len(self.queue) >= self.capacity

    @property
    def dirt(self):
        return self._dirt

    @dirt.setter
    def dirt(self, value):
        self._dirt = min(max(value, 0), self.dirt_limit)

    @property
    def over_dirt_limit(self):
        return self.dirt > self.dirt_limit

    @property
    def failure_rate(self):
        from model import World
        rate =  1 / (self.capacity * self.duration)
        if World().ruziland:
            rate *= RUZILAND_FAILURE_RATE_FACTOR
        return rate

    @property
    def time_cleaning(self):
        max_cleaning_time = RIDE_MAX_CLEANING_TIME
        return min(self.dirt - self.dirt_limit, max_cleaning_time)

    def out_of_service(self):
        self.closed = True
        self._time_begin_oos = Simulation().time.raw()

    def back_in_service(self):
        self.closed = False
        new_t = Simulation().time.raw()
        self._times_oos = new_t - self._time_begin_oos
        self._time_begin_oos = new_t


class Restaurant(Entity):
    def __init__(self, id, name, capacity, adult_cost,
                 child_cost, max_duration):
        self.id = int(id)
        self.name = name
        self.capacity = int(capacity)
        self.adult_cost = int(adult_cost)
        self.child_cost = int(child_cost)
        self.max_duration = int(max_duration)

        self.rides = {ride for restaurant, ride in get_associations()
                      if restaurant == self.id}

    @property
    def time_cooking_adult(self):
        return int(expovariate(RESTAURANT_ADULT_PREP))

    @property
    def time_cooking_child(self):
        return int(expovariate(RESTAURANT_CHILD_PREP))
