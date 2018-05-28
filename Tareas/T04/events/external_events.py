from random import expovariate, uniform, random

from events import Event
from model import World, Nebiland
from sim import Simulation

from params import (RUZILAND_BEGIN_LOWER, RUZILAND_BEGIN_UPPER,
                    RAIN_RATE, RAIN_DURATION, RUZILAND_MONDAY_SKIP,
                    RUZILAND_CHANCE)


def schedule_external_events():
    """
    Schedules ocurrence of all external events
    """
    schedule_rainy_day()
    schedule_ruziland_invasion()
    schedule_school_day()

##########################
# Rain day


def schedule_rainy_day():
    """
    Schedules beginning of rain day event
    """
    event_begin = Event("BeginRainyDay", World(), begin_rainy_day)
    Simulation().schedule(event_begin, time=int(expovariate(RAIN_RATE)*60*24))


def begin_rainy_day(world):
    """
    Schedules end of rain day event
    """
    world.raining = True
    event_end = Event("EndRainyDay", World(), end_rainy_day)
    Simulation().schedule(event_end, delta=RAIN_DURATION.raw())


def end_rainy_day(world):
    """
    Ends rainy day and schedules next beginning
    """
    world.raining = False
    schedule_rainy_day()


##########################
# Ruziland invasion

def schedule_ruziland_invasion():
    """
    Schedules ruziland invasion on a monday betwee the times
    RUZILAND_BEGIN_LOWER and RUZILAND_BEGIN_UPPER
    """
    # Since each simulation lasts only a week, we can just use a conditional!
    event = Event("BeginRuzilandInvasion", World(), begin_ruziland)
    if random() < RUZILAND_CHANCE / RUZILAND_MONDAY_SKIP:
        lower = RUZILAND_BEGIN_LOWER
        upper = RUZILAND_BEGIN_UPPER
        Simulation().schedule(event, time=int(
            uniform(lower.time(), upper.time()))
        )


def begin_ruziland(world):
    """
    Event Callback

    Schedules end of ruziland invasion at the closing time of the day
    """
    event = Event("EndRuzilandInvasion", World(), lambda x: None)
    Simulation().schedule(event, time=Nebiland().closing_time_today)


##########################
# School day

def schedule_school_day():
    """
    kek
    """
    pass
