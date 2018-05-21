from events.events_base import Event
from model import nebiland

def foo_clientArriveAtPark(entity, time):
    nebiland.entrance_queue.enter(entity)
    Scheduler.schedule(time)

def foo_clientEnterRide(entity, world_state):
    nebiland.
    
clientArriveAtPark = Event("Client Arrives at Park", foo_clientArriveAtPark)
