from random import expovariate, uniform, random

from events import Event
from model import World, Nebiland
from sim import Simulation


def schedule_external_events():
    schedule_rainy_day()
    schedule_ruziland_invasion()
    schedule_school_day()

##########################
# Rain day


def schedule_rainy_day():
    event_begin = Event("BeginRainyDay", World(), begin_rainy_day)
    Simulation().schedule(event_begin, time=int(expovariate(1/20)*60*24))


def begin_rainy_day(world):
    world.raining = True
    event_end = Event("EndRainyDay", World(), end_rainy_day)
    Simulation().schedule(event_end, delta=60*24)


def end_rainy_day(world):
    world.raining = False
    schedule_rainy_day()


##########################
# Ruziland invasion

def schedule_ruziland_invasion():
    # Since each simulation lasts only a week, we can just use a conditional!
    event = Event("BeginRuzilandInvasion", World(), begin_ruziland)
    if random() < 0.5 * 0.25:
        Simulation().schedule(event, time=uniform(10*60, 14*60 + 30))


def begin_ruziland():
    event = Event("EndRuzilandInvasion", World(), lambda x: None)
    Simulation().schedule(event, time=Nebiland().closing_time_today)


##########################
# School day

def schedule_school_day():
    pass

