from random import expovariate
from functools import partial

from events import Event
from sim import Simulation
from model import Nebiland
from misc_lib import Logger

from params import (TECH_FIX_TIME, TECH_TRAVEL_TIME,
                    CLEANER_TRAVEL_TIME, PARK_OPEN_TIME,
                    PARK_CLOSE_TIME)


def schedule_initial_park_events():
    """
    Schedules initial ride failures
    """
    for ride in Nebiland().attractions:
        schedule_ride_failure(ride)
        schedule_ride_start(ride)

    schedule_lunch_times()


def schedule_ride_failure(ride):
    """
    Schedules a failure to ocurr only during opening hours
    """
    event = Event("RideFails", ride, lambda r: r.fail(Simulation().time))
    fail_time = (int(expovariate(ride.failure_rate)) +
                 Simulation().time.time())

    open_time = PARK_OPEN_TIME.time()
    close_time = PARK_CLOSE_TIME.time()

    # This only ocurrs on the initial scheduling, I believe. Turns an
    # event scheduled at 01:04 into one scheduled at 11:04
    if fail_time < open_time:
        fail_time += open_time

    # Wraps an event scheduled after opening hours into the opening
    # hours of the next day
    if fail_time > close_time:
        fail_time = fail_time - close_time + open_time
        fail_time += Simulation().time.day_ts()

    fail_time += Simulation().time.day_ts()

    Simulation().schedule(event, time=fail_time)


# Lunch times


def schedule_lunch_times():
    """
    Schedules lunch times for every worker for every day of the week
    """
    from model import WorkerManager
    for worker in WorkerManager()._all_workers:
        # Schedule it for all days
        for i in range(7):
            event = Event("WorkerGoesForLunch", worker,
                          worker_begin_lunch_time)
            lunch_time = i*60*24 + worker.lunch_hour*60
            Simulation().schedule(event, time=lunch_time)


def worker_begin_lunch_time(worker):
    # TODO: Worker must finish what they were doing
    worker.close_down_responsibilities()
    event = Event("WorkerFinishesLunch", worker, worker_end_lunch_time)
    Simulation().schedule(event, delta=59)


def worker_end_lunch_time(worker):
    worker.open_up_responsibilities()


# Fixers

def ride_call_for_fix(ride):
    """
    Event callback: Generates a ticket to fix the given ride.

    Schedules a conditional event activated on the ticket being
    processed by the park's worker manager
    """
    ride.out_of_service()
    Logger().clean_calls_per_day[Simulation().time.day] += 1
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
    foo = partial(ride_finish_fix, ticket=ticket)
    event = Event("FixerFixesRide", ride, foo,
                  extra_info=lambda: ticket.worker)
    Simulation().schedule(event, delta=TECH_FIX_TIME)


def ride_finish_fix(ride, ticket):
    """
    Event callback: Fixer has finished fix and sets the work ticket to
    done.

    Schedules the next ride failure
    """
    ticket.done()
    ride.fix(Simulation().time)
    schedule_ride_failure(ride)
    schedule_ride_start(ride)

# Cleaners


def ride_call_for_clean(ride):
    """
    Event callback: Generates a ticket to clean the given ride.

    Schedules a conditional event activated on the ticket being
    processed by the park's worker manager
    """
    ride.out_of_service()
    Logger().clean_calls_per_day[Simulation().time.day] += 1
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
    foo = partial(finish_cleaning, ticket=ticket)
    event = Event("CleanerFixesRide", ride, foo)
    Simulation().schedule(event, delta=ride.time_cleaning)


def finish_cleaning(ride, ticket):
    """
    Event callback: Finish clean and get ride started again
    """
    ticket.done()
    schedule_ride_start(ride)

# Operators


def operator_check_ride(ride):
    """
    Event callback: Operator checks the state of the ride before staring.

    Schedules a fix/clean request or a ride start
    """
    # Bookkeep ride check
    Simulation().schedule(Event("RideCheck", ride, lambda e: None,
                                extra_info=lambda: str(ride.operator)))

    if ride.over_dirt_limit:
        ride_call_for_clean(ride)
        return False
    if ride.failed and not ride._serviced:
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

    if not Nebiland().open:
        # Bookkeep ride closed
        Simulation().schedule(Event("RideClosedForTheDay", ride,
                                    lambda e: None))

        event = Event("RideReopens", ride, schedule_ride_start)
        mult = Simulation().time.raw() != 0  # Fixes weird behavior at time 0
        time = Simulation().time.day_ts() + 60*24*mult + PARK_OPEN_TIME.time()
        Simulation().schedule(event, time)
        return

    # Check the ride and reschedule the next check
    if not operator_check_ride(ride):
        # Ride must be serviced and can't be ridden right now
        return

    # Schedule the beginning
    event = Event("RideStartsFullCapacity", ride, lambda r: ride.start())
    Simulation().schedule(event, condition=ride.can_begin)


def schedule_forced_start(ride):
    """
    Schedules forced start of the ride once at least one person is in
    the queue.

    Obsoletable if ride has already started due to the queue being at
    least as long as the ride's capacity
    """
    event = Event("RideStartTimesUp", ride, lambda r: ride.start())
    Simulation().schedule(event, delta=ride.max_time,
                          obsolete_if=lambda r: r.started)
