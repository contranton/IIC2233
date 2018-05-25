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
    def __init__(self, adult=True):
        self.name = fkr.name()

        if adult:
            self.height = normalvariate(170, 8)
        else:
            self.height = normalvariate(120, 15)

        self.has_left = False

        self._energy = 1
        self._hunger = uniform(0.01, 0.25)
        self._nausea = 0
        self._budget = 0

        self._children = []

    def __repr__(self):
        return "Client({})".format(self.name)
        
    @property
    def patience(self):
        return normalvariate(10+30*self._energy, 5)

    @property
    def budget(self):
        return self._budget

    @budget.setter
    def budget(self, value):
        self._budget = value


class Child(Entity):
    def __init__(self, parent):
        parent._children.append(self)


class Worker(Entity):
    manager = WorkerManager()


class Attraction(Entity):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.dirt = 0

    @property
    def time_failures(self):
        rate = 1 / (self.capacity * self.duration)
        return expovariate(rate)

    @property
    def time_cleaning(self):
        max_cleaning_time = 10
        return min(self.dirt - self.dirt_limit, max_cleaning_time)


class Restaurant(Entity):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    @property
    def time_cooking_adult(self):
        return expovariate(6)

    @property
    def time_cooking_child(self):
        return expovariate(4)
