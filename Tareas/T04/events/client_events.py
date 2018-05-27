from random import random, expovariate, choice
from functools import partial

from events import Event
from entity import Client, Child
from sim import Simulation
from model import Nebiland, World
from fileio import get_arrivals
from misc_lib import datetime_to_time, Logger

# I f****ng love emacs
from params import (PARK_OPEN_TIME, PARK_CLOSE_TIME,
                    CLIENT_ENERGY_IMMEDATE_LEAVE_THRESHOLD,
                    CLIENT_ENERGY_MIGHT_LEAVE_THRESHOLD,
                    CLIENT_ENERGY_P_MIGHT_LEAVE,
                    CLIENT_CHOOSE_RESTAURANT_MULT, CLIENT_P_RIDE,
                    CLIENT_DECISION_TIME, CLIENT_BREAK_TIME,
                    RESTAURANT_ADULT_PREP, RESTAURANT_CHILD_PREP,
                    RESTAURANT_HUNGER_DELTA, RESTAURANT_ENERGY_DELTA,
                    RESTAURANT_AFTER_RIDE_NAUSEA, RIDE_CHILD_NAUSEA,
                    RIDE_ADULT_NAUSEA, RIDE_VOMIT_DIRT,
                    RIDE_DIRT_DELTA, SCHOOL_DAY_MIN_CHILDREN)


def schedule_arrivals():
    for day, time, budget, children in get_arrivals():
        # Create new clients
        client = Client()
        client.budget = budget
        for i in range(children):
            client.add_child(Child())

        # Log clients to DAQ
        Logger().all_clients.append(client)

        # Client enters
        event_enter = Event("ClientArrives", client, client_enter_park)
        Simulation().schedule(event_enter, time=datetime_to_time(day, time))


def client_enter_park(client):
    # Ensures limit and capacity as well as school day restrictions
    leave_event = lambda reason: Event("ClientForbiddenEntry{}".format(reason),
                                       client, client_cant_enter)
    # Client arrives too late
    if (Simulation().time.raw() % (60*24)) > PARK_CLOSE_TIME.raw():
        event = leave_event("TooLate")
        Simulation().schedule(event)
        return

    if not Nebiland().has_capacity:
        event = leave_event("ParkIsFull")
        Simulation().schedule(event)
        return

    # If adult doesn't have enough children during a school day
    if World().school_day and len(client.children) < SCHOOL_DAY_MIN_CHILDREN:
        event = leave_event("TooFewChildrenInSchoolDay")
        Simulation().schedule(event)
        return

    # Client enters just fine
    c_id = Nebiland().client_enters(client.name, client.num_children)
    client.client_id = c_id

    client_decide_next_action(client)

    # Schedule forced leave at the closing time
    # event_leave = Event("ClientLeaveDueToClosing", client, client_leave)
    # Simulation().schedule(event_leave, time=Nebiland().closing_time_today,
    #                      obsolete_if=lambda client: client.has_left)


def ensure_park_open(client):
    if (Simulation().time.raw() % (60*24)) > PARK_CLOSE_TIME.raw():
        event_leave = Event("ClientLeaveDueToClosing", client, client_leave)
        Simulation().schedule(event_leave)
        return False
    return True


def client_decide_next_action(client):
    """
    Decides what a client will do next
    """

    # If client has left an installation but park has closed, must leave
    if not ensure_park_open(client):
        return

    # If clients don't have enough energy, they leave
    min_energy = client.minimum_energy
    if min_energy <= CLIENT_ENERGY_IMMEDATE_LEAVE_THRESHOLD:
        event = Event("ClientLeavesDueToEnergy", client, client_leave)
        Simulation().schedule(event)
        return
    elif client.any_energy_less_than(CLIENT_ENERGY_MIGHT_LEAVE_THRESHOLD):
        if random() < CLIENT_ENERGY_P_MIGHT_LEAVE:
            event = Event("ClientLeavesDueToEnergy", client, client_leave)
            Simulation().schedule(event)

    # Randomly choose the next place to go
    # No chance of going to a restaurant if they haven't gone to the
    # necessary ride
    restaurant_p = client.average_hunger * CLIENT_CHOOSE_RESTAURANT_MULT
    restaurant_p *= Nebiland().any_valid_restaurants(client.rides_ridden)
    queue_p = client.willing_to_queue * CLIENT_P_RIDE
    p = random()
    if p < queue_p:
        # Goto ride
        ride = choose_ride(client)
        foo = partial(client_goto_ride, ride=ride)
        event = Event("ClientGoesToRide", client, foo)
        Simulation().schedule(event, delta=CLIENT_DECISION_TIME)
    elif queue_p < p < queue_p + restaurant_p:
        # Goto restaurant
        event = Event("ClientGoesToEat", client, client_goto_restaurant)
        Simulation().schedule(event, delta=CLIENT_DECISION_TIME)
    else:
        # Rest
        event = Event("ClientBeginsBreak", client, client_take_break)
        Simulation().schedule(event, delta=CLIENT_DECISION_TIME)


def client_leave(client):
    # Client exits park due to lack of budget
    Nebiland().client_exits(client.client_id)
    client.has_left = True


def client_cant_enter(client):
    # Client not allowed into the park
    pass


def client_goto_restaurant(client):
    # Client might not get to the installation in time before park closes
    if not ensure_park_open(client):
        return

    # Restaurant selection
    valid_restaurants = Nebiland().get_valid_restaurants(client.rides_ridden)
    restaurant = choice(valid_restaurants)

    # Food preparation
    time_entered = Simulation().time.raw()
    in_restaurant = partial(client_in_restaurant,
                            restaurant=restaurant,
                            time_entered=time_entered)
    event = Event("ClientPreparesFood", client, in_restaurant)
    Simulation().schedule(event, delta=restaurant.time_cooking_adult)
    for child in client.children:
        event = Event("ChildPreparesFood", child, lambda e: None)
        Simulation().schedule(event, delta=restaurant.time_cooking_child)


def client_in_restaurant(client, restaurant, time_entered):
    event = Event("ClientLeavesRestaurant", client, client_leave_restaurant)
    max_time = restaurant.max_duration + time_entered
    Simulation().schedule(event, time=max_time)


def client_leave_restaurant(client):
    if client.just_rode:
        client.nausea += RESTAURANT_AFTER_RIDE_NAUSEA
        client.increase_children_nausea(RESTAURANT_AFTER_RIDE_NAUSEA)
    client.raise_all_hungers(RESTAURANT_HUNGER_DELTA)
    client.raise_all_energies(RESTAURANT_ENERGY_DELTA)
    client.willing_to_queue = True
    client.just_rode = False
    client_decide_next_action(client)


def client_take_break(client):
    event = Event("ClientFinishesBreak", client, client_finish_break)
    Simulation().schedule(event, delta=CLIENT_BREAK_TIME)


def client_finish_break(client):
    client.rest()
    client.willing_to_queue = True
    client.just_rode = False
    client_decide_next_action(client)


def choose_ride(client):
    for ride in Nebiland().attractions_by_queue_length:
        if ride in client.cant_ride_list:
            continue
        return ride


def client_goto_ride(client, ride):
    # Client might not get to the installation in time before park closes
    if not ensure_park_open(client):
        return

    can_ride = client.any_height_below(ride.min_height)

    if not can_ride:
        foo = partial(client_cant_ride, ride=ride)
        event = Event("ClientNotAllowedInRide", client, foo)
        Simulation().schedule(event)
        return
    ################

    enter_ride = partial(client_enter_ride_queue, ride=ride)
    event = Event("ClientEntersQueueForRide", client, enter_ride)
    Simulation().schedule(event)


def client_cant_ride(client, ride):
    client.cant_ride_list.append(ride)
    client_decide_next_action(client)


def client_enter_ride_queue(client, ride):
    # Schedule conditional event whereby client loses patience
    exit_queue = partial(client_exits_queue, ride=ride)
    event = Event("ClientLosesPatienceInQueue", client, exit_queue)
    Simulation().schedule(event, delta=int(client.patience),
                          obsolete_if=lambda client: client.got_on)

    ride.add_to_queue(client)


def callback_enter_ride(client, ride):
    # Log the event of having finished the queue
    Simulation().schedule(Event("ClientEntersRide", client, lambda e: None))
    client.got_on = True

    # Schedule getting off the ride
    leave_ride = partial(client_leaves_ride, ride=ride)
    event = Event("ClientLeavesRide", client, leave_ride)
    Simulation().schedule(event, delta=ride.duration)


def client_exits_queue(client, ride):
    client.got_on = False
    client.willing_to_queue = False
    ride.remove_from_queue(client)
    client_decide_next_action(client)


def client_leaves_ride(client, ride):
    client.rides_ridden.add(ride)
    client.nausea += RIDE_ADULT_NAUSEA
    client.increase_children_nausea(RIDE_CHILD_NAUSEA)
    client.just_rode = True
    ride.dirt += RIDE_VOMIT_DIRT * client.num_throw_up
    ride.dirt += RIDE_DIRT_DELTA
    client_decide_next_action(client)
