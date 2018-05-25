from random import random

from events import Event
from entity import Client, Child
from sim import Simulation
from model import Nebiland, World
from fileio import get_arrivals
from misc_lib import datetime_to_time


def schedule_arrivals():
    for day, time, budget, children in get_arrivals():
        # Create new clients
        client = Client()
        client.budget = budget
        for i in range(children):
            client.add_child(Child())

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
    event_leave = Event("ClientLeaveDueToClosing", client, client_leave)
    Simulation().schedule(event_leave, time=Nebiland().closing_time_today,
                          obsolete_if=lambda client: client.has_left)


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
    restaurant_probability = client.average_hunger * 0.3
    p = random()
    if p < 0.7:
        # Goto ride
        event = Event("ClientGoesToRide", client, client_goto_ride)
        Simulation().schedule(event, delta=10)
    elif 0.7 < p < 0.7 + restaurant_probability:
        # Goto restaurant
        event = Event("ClientGoesToEat", client, client_goto_restaurant)
        Simulation().schedule(event, delta=10)
    else:
        # Rest
        event = Event("ClientTakesBreak", client, client_take_break)
        Simulation().schedule(event, delta=10)


def client_leave(client):
    # Client exits park due to lack of budget
    Nebiland().client_exits(client.client_id)


def client_cant_enter(client):
    # Client not allowed into the park or queue
    pass


def client_goto_restaurant(client):
    # Client might not get to the installation in time before park closes
    if not ensure_park_open(client):
        return

    ############
    # Restaurant Logic
    #available_restaurants = Nebiland().get_valid_restaurants(client.rides_ridden)

    #

    event = Event("ClientLeavesRestaurant", client, client_leave_restaurant)
    Simulation().schedule(event, delta=100)


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

    ################

    event = Event("ClientLeavesRide", client, client_leaves_ride)
    Simulation().schedule(event, delta=100)


def client_leaves_ride(client):
    client_decide_next_action(client)
