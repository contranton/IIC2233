from random import randrange

from sim import Simulation
from events import Event
from entity import Entity

capacity = 50
i = 0


def foo_my_event(entity):
    global i
    global capacity
    if i < capacity:
        print("Person %i arrives woohoo" % i)
        i += 1
        object = Entity()
        object.id = i
        return [(Event("Lol", object, foo_my_event), 10),
                (Event("Bye", object, lambda e: print("Person %i leaves awwww" % e.id)), randrange(100, 200))]

    return [(Event("Aw", None, foo_turned_away), 100)]


def foo_turned_away(entity):
    print("Park has closed")
    return None


if __name__ == '__main__':
    import pdb
    sim = Simulation()
    sim.schedule(Event("Test", None, foo_my_event), 10)
