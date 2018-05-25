from world import IWorld
from misc_lib import Singleton

from random import normalvariate, expovariate, uniform

from faker import Faker
fkr = Faker()


class Entity:
    world = property(lambda _: IWorld().world)


class WorkerManager(metaclass=Singleton):
    workers = []
    

class Client(Entity):
    def __init__(self):
        self.name = fkr.name()
        self._energy = 1
        self._hunger = uniform(0.01, 0.25)
        self._nausea = 0
        self._budget = 0

        
        self.height = normalvariate(170, 8)
        self.has_left = False
        self._children = []

        self.client_id = None


    def __repr__(self):
        return "Client({})".format(self.name)

    def add_child(self, child):
        child.adult = self
        self._children.append(child)

    @property
    def patience(self):
        return normalvariate(10+30*self._energy, 5)

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
    def minimum_energy(self):
        return min(self._all_energies)

    def any_energy_less_than(self, value):
        return any(map(lambda x: x < value, self._all_energies))

    @property
    def average_hunger(self):
        return sum(self._all_hungers) / (self.num_children + 1)

    def rest(self):
        self._energy = min(self._energy + 0.2, 1)
        for c in self._children:
            c._energy = min(c._energy + 0.2, 1)


class Child(Entity):
    def __init__(self):
        self.name = fkr.name()
        self._energy = 1
        self._hunger = uniform(0.01, 0.25)
        self._nausea = 0
        self._budget = 0

        self.height = normalvariate(120, 15)
        self.adult = None


class Worker(Entity):
    manager = WorkerManager()


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
        self.min_height = int(min_height)

    @property
    def time_failures(self):
        rate = 1 / (self.capacity * self.duration)
        return expovariate(rate)

    @property
    def time_cleaning(self):

        max_cleaning_time = 10
        return min(self.dirt - self.dirt_limit, max_cleaning_time)


class Restaurant(Entity):
    def __init__(self, id, name, capacity, adult_cost,
                 child_cost, max_duration):
        self.id = int(id)
        self.name = name
        self.capacity = int(capacity)
        self.adult_cost = int(adult_cost)
        self.child_cost = int(child_cost)
        self.max_duration = int(max_duration)

    @property
    def time_cooking_adult(self):
        return expovariate(6)

    @property
    def time_cooking_child(self):
        return expovariate(4)
