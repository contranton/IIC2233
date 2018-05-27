from random import expovariate
from functools import partial

from events import Event
from sim import Simulation
from model import Nebiland

from params import TECH_FIX_TIME, TECH_TRAVEL_TIME, PARK_OPEN_TIME


def schedule_initial_park_events():
    # TODO: Failures only in opening hours man
    for ride in Nebiland().attractions:
        event = Event("RideFails", ride, ride_call_for_fix)
        Simulation().schedule(event,
                              time=PARK_OPEN_TIME.raw() +
                              Simulation().time.raw() // (60*24) +
                              int(expovariate(ride.failure_rate)))

        schedule_ride_start(ride)


# Fixers

def ride_call_for_fix(ride):
    ticket = Nebiland().add_ticket(ride, "fix")
    foo = partial(ride_fixer_arrive, ticket=ticket)
    event = Event("FixerAssignedToRide", ride, foo,
                  extra_info=lambda: ticket.worker)

    Simulation().schedule(event, condition=ticket)


def ride_fixer_arrive(ride, ticket):
    #from model import WorkerManager
    #print(WorkerManager()._all_workers)

    foo = partial(ride_fixer_fix, ticket=ticket)
    event = Event("FixerArrivedAtRide", ride, foo,
                  extra_info=lambda: ticket.worker)
    Simulation().schedule(event, delta=TECH_TRAVEL_TIME)


def ride_fixer_fix(ride, ticket):
    event = Event("FixerFixesRide", ride, lambda e: ticket.done(),
                  extra_info=lambda: ticket.worker)
    Simulation().schedule(event, delta=TECH_FIX_TIME)


# Cleaners


def ride_call_for_clean(ride):
    ticket = Nebiland().add_ticket(ride, "clean")
    foo = partial(ride_cleaner_arrive, ticket=ticket)
    event = Event("CleanerAssignedToRide", ride, foo)
    Simulation().schedule(event, condition=ticket)


def ride_cleaner_arrive(ride, ticket):
    foo = partial(ride_cleaner_clean, ticket=ticket)
    event = Event("CleanerArrivedAtRide", ride, foo)
    Simulation().schedule(event, delta=CLEANER_TRAVEL_TIME)


def ride_cleaner_clean(ride, ticket):
    event = Event("CleanerFixesRide", ride,
                  lambda: ticket.done())
    Simulation().schedule(event, delta=ride.time_cleaning)


# Operators

def operator_check_ride(ride):
    if ride.over_dirt_limit:
        ride_call_for_clean(ride)
        return False
    # TODO: WILL RIDE FAIL??
    if False:
        ride_call_for_fix(ride)
        return False
    # TODO: Reschedule this
    return True


# Rides

def schedule_ride_start(ride):
    event = Event("RideStarts", ride, lambda r: ride.start())
    Simulation().schedule(event, condition=ride.can_begin)
