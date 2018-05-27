from random import expovariate
from functools import partial

from events import Event
from sim import Simulation
from model import Nebiland

from params import TECH_FIX_TIME, TECH_TRAVEL_TIME, PARK_OPEN_TIME


def schedule_initial_park_events():
    """
    Schedules initial ride failures
    """
    # TODO: Failures only in opening hours man
    for ride in Nebiland().attractions:
        event = Event("RideFails", ride, ride_call_for_fix)
        Simulation().schedule(event,
                              time=PARK_OPEN_TIME.raw() +
                              Simulation().time.raw() // (60*24) +
                              int(expovariate(ride.failure_rate)))
        schedule_ride_start(ride)

    schedule_lunch_times()

# Lunch times


def schedule_lunch_times():
    from model import WorkerManager
    for worker in WorkerManager()._all_workers:
        event = Event("WorkerGoesForLunch", worker, worker_begin_lunch_time)
        # Schedule it for all days
        for i in range(5):
            Simulation().schedule(event, time=i*60*24 + worker.lunch_hour*60)


def worker_begin_lunch_time(worker):
    worker.close_down_responsabilities()
    event = Event("WorkerFinishesLunch", worker, worker_end_lunch_time)
    Simulation().schedule(event, delta=59)


def worker_end_lunch_time(worker):
    worker.open_up_responsabilities()


# Fixers

def ride_call_for_fix(ride):
    """
    Event callback: Generates a ticket to fix the given ride.

    Schedules a conditional event activated on the ticket being
    processed by the park's worker manager
    """
    ride.out_of_service()
    ticket = Nebiland().add_ticket(ride, "fix")
    foo = partial(ride_fixer_arrive, ticket=ticket)
    event = Event("FixerAssignedToRide", ride, foo,
                  extra_info=lambda: ticket.worker)

    Simulation().schedule(event, condition=ticket)


def ride_fixer_arrive(ride, ticket):
    """
    Event callback: Technician has been called to fix ride

    Takes ticket assosciated with the fixing request

    Schedules arrival of technician at ride
    """

    foo = partial(ride_fixer_fix, ticket=ticket)
    event = Event("FixerArrivedAtRide", ride, foo,
                  extra_info=lambda: ticket.worker)
    Simulation().schedule(event, delta=TECH_TRAVEL_TIME)


def ride_fixer_fix(ride, ticket):
    """
    Event callback: Technician has arrived to the ride and begins
    fixing

    Takes ticket assosciated with the fixing request

    Schedules end of fix by setting the ticket as done
    """
    event = Event("FixerFixesRide", ride, lambda e: ticket.done(),
                  extra_info=lambda: ticket.worker)
    Simulation().schedule(event, delta=TECH_FIX_TIME)


# Cleaners


def ride_call_for_clean(ride):
    """
    Event callback: Generates a ticket to clean the given ride.

    Schedules a conditional event activated on the ticket being
    processed by the park's worker manager
    """
    ride.out_of_service()
    ticket = Nebiland().add_ticket(ride, "clean")
    foo = partial(ride_cleaner_arrive, ticket=ticket)
    event = Event("CleanerAssignedToRide", ride, foo)
    Simulation().schedule(event, condition=ticket)


def ride_cleaner_arrive(ride, ticket):
    """
    Event callback: Cleaner has been called to clean ride

    Takes ticket assosciated with the cleaning request

    Schedules arrival of technician at ride
    """
    foo = partial(ride_cleaner_clean, ticket=ticket)
    event = Event("CleanerArrivedAtRide", ride, foo)
    Simulation().schedule(event, delta=CLEANER_TRAVEL_TIME)


def ride_cleaner_clean(ride, ticket):
    """
    Event callback: Cleaner has arrived to the ride and begins
    cleaning

    Takes ticket assosciated with the cleaning request

    Schedules end of cleaning by setting the ticket as done
    """
    event = Event("CleanerFixesRide", ride,
                  lambda: ticket.done())
    Simulation().schedule(event, delta=ride.time_cleaning)


# Operators

def operator_check_ride(ride):
    """
    Event callback: Operator checks the state of the ride before staring.

    Schedules a fix/clean request or a ride start
    """
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
    """
    Event callback: Schedules next ride start.

    Conditional on the ride's readiness.
    """
    if not operator_check_ride(ride):
        # Ride must be serviced and can't be ridden right now
        event = Event("CheckRide", ride, schedule_ride_start)
        Simulation().schedule(event, condition=lambda: not ride.closed)
        return
    event = Event("RideStarts", ride, lambda r: ride.start())
    Simulation().schedule(event, condition=ride.can_begin)
