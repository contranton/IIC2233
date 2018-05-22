from events.events_base import Event
# from model import nebiland
from sim import current_sim


def foo_clientArriveAtPark(entity, time):
    #  nebiland.entrance_queue.enter(entity)
    
    print("HELLO NEW PERSON")
    event = Event("Client Arrives at Park", entity, foo_clientArriveAtPark)
    current_sim().schedule(event, time=100)


def foo_clientEnterRide(entity, world_state):
    pass


EventClientArriveAtPark = Event("Client Arrives at Park", None,  foo_clientArriveAtPark)
