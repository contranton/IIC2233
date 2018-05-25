from events import Event
from entity import Client, Child
from sim import Simulation
#from model import Nebiland
from fileio import get_arrivals
from misc_lib import datetime_to_time


def schedule_arrivals():
    for day, time, budget, children in get_arrivals():
        # Create new clients
        client = Client()
        client.budget = budget
        for i in range(children):
            child = Child(client)

        # If client arrives too late
        if int(time[:2]) >= 19:
            event_blocked = Event("ClientForbiddenEntry", client, client_cant_enter)
            Simulation().schedule(event_blocked, time=datetime_to_time(day, time))
            continue
            
        # Client enters
        event_enter = Event("ClientArrives", client, client_enter_park)
        Simulation().schedule(event_enter, time=datetime_to_time(day, time))

        # Client leaves
        event_leave = Event("ClientLeaveDueToClosing", client, client_leave)
        Simulation().schedule(event_leave, time=datetime_to_time(day, "19:00"),
                              obsolete_if=lambda client: client.has_left)

def client_enter_park(client):
    # Ensures limit and capacity as well as school day restrictions
    pass
        
def client_decide_next_action(client):
    # client makes decision of what thing to do
    pass

def client_leave(client):
    pass

def client_cant_enter(client):
    # Client not allowed into the park or queue
    pass
