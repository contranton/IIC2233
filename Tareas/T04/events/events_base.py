from simtime import timebase


def counter(start):
    i = start
    while True:
        yield i
        i += 1

class Event(object):
    """
    Main abstract event object from which certain event implementaions
    inherit
    """

    id_counter = counter(1)

    def __init__(self, name, entity, function, time=timebase.origin):
        self.name = name
        self.function = function
        self.entity = entity
        self.time = time
        self.event_id = next(Event.id_counter)

    def run(self):
        # log
        # all sorts of underlying boilerplate and whatnot
        self.function(self.entity, self.time)

    def update_time(self, time_val):
        self.time = time_val

    def __lt__(self, other):
        return self.time < other.time
