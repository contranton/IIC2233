from random import random, expovariate, choice
from functools import partial

from events import Event
from entity import Client, Child
from sim import Simulation
from model import Nebiland, World
from fileio import get_arrivals
from misc_lib import datetime_to_time, Logger


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

        # Client leaves


def client_enter_park(client):
    # Ensures limit and capacity as well as school day restrictions
    leave_event = lambda reason: Event("ClientForbiddenEntry{}".format(reason),
                                       client, client_cant_enter)
    # Client arrives too late
    if Simulation().time.hour >= 19:
        event = leave_event("TooLate")
        Simulation().schedule(event)
        return

    if not Nebiland().has_capacity:
        event = leave_event("ParkIsFull")
        Simulation().schedule(event)
        return

    # If adult doesn't have enough children during a school day
    if World().school_day and len(client.children) < 10:
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
    if Simulation().time.hour >= 19:
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
    if min_energy == 0:
        event = Event("ClientLeavesDueToEnergy", client, client_leave)
        Simulation().schedule(event)
    if client.any_energy_less_than(0.1):
        if random() < 0.5:
            event = Event("ClientLeavesDueToEnergy", client, client_leave)
            Simulation().schedule(event)

    # Randomly choose the next place to go
    # No chance of going to a restaurant if they haven't gone to the
    # necessary ride
    restaurant_p = client.average_hunger * 0.3
    restaurant_p *= Nebiland().any_valid_restaurants(client.rides_ridden)
    p = random()
    if p < 0.7:
        # Goto ride
        event = Event("ClientGoesToRide", client, client_goto_ride)
        Simulation().schedule(event, delta=10)
    elif 0.7 < p < 0.7 + restaurant_p:
        # Goto restaurant
        event = Event("ClientGoesToEat", client, client_goto_restaurant)
        Simulation().schedule(event, delta=10)
    else:
        # Rest
        event = Event("ClientFinishesBreak", client, client_take_break)
        Simulation().schedule(event, delta=10)


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
    time_entered = Simulation().time
    in_restaurant = partial(client_in_restaurant,
                            restaurant=restaurant,
                            time_entered=time_entered)
    event = Event("ClientPreparesFood", client, in_restaurant)
    Simulation().schedule(event, delta=int(expovariate(1/6)))
    for child in client.children:
        event = Event("ChildPreparesFood", child, lambda e: None)
        Simulation().schedule(event, delta=int(expovariate(1/4)))


def client_in_restaurant(client, restaurant, time_entered):
    event = Event("ClientLeavesRestaurant", client, client_leave_restaurant)
    max_time = restaurant.max_duration + time_entered
    Simulation().schedule(event, time=max_time)


def client_leave_restaurant(client):
    client_decide_next_action(client)


def client_take_break(client):
    client.rest()
    client_decide_next_action(client)


def client_goto_ride(client):
    # Client might not get to the installation in time before park closes
    if not ensure_park_open(client):
        return

    ################
    # Ride Logic
    chosen_ride = None
    for ride in Nebiland().attractions_by_queue_length:
        if ride in client.cant_ride_list:
            continue
        chosen_ride = ride

    can_ride = client.any_height_below(ride.min_height)

    if not can_ride:
        client.cant_ride_list.append(ride)
        client_decide_next_action(client)
        return
    ################

    enter_ride = partial(client_enter_ride_queue, ride=ride)
    event = Event("ClientEntersQueueForRide", client, enter_ride)
    Simulation().schedule(event)
    

def client_enter_ride_queue(client, ride):
    # Schedule conditional event whereby client loses patience
    event = Event("ClientLosesPatienceInQueue", client, client_exits_queue)
    Simulation().schedule(event, delta=client.patience,
                          obsolete_if=lambda client: client.got_on)

    #Nebiland().add_to_queue(ride, client)

    # TODO:
    # TODO: Implement Queing system. TODAY PLS
    # TODO: 


def client_ride_over(client, ride):
    client.got_on = True
    client.rides_ridden.add(ride)
    event = Event("ClientLeavesRide", client, client_leaves_ride)
    Simulation().schedule(event, delta=ride.duration)


def client_exits_queue(client):
    client.got_on = False
    client_decide_next_action(client)


def client_leaves_ride(client):
    client_decide_next_action(client)
