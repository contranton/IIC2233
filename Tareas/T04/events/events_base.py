from abc import abstractmethod
from collections import counter


from timebase.time import timebase


class Event(object):
    """
    Main abstract event object from which certain event implementaions
    inherit
    """

    id_counter = counter(1)

    def __init__(self, time=timebase.origin):
        self.event_id = next(Event.id_counter)

    def run(self):
        # log
        # all sorts of underlying boilerplate and whatnot
        self.execute()

    @abstractmethod
    def execute(self):
        pass
