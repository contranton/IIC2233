from sim import Simulation
from misc_lib import Logger, timestamp_to_datetime


class Event(object):

    def __init__(self, name, entity, function, extra_info=None):
        self.name = name
        self.entity = entity
        self.function = function
        self.update_time(0)

        if callable(extra_info):
            self.extra_info = extra_info
        else:
            self.extra_info = lambda: extra_info if extra_info else ""

    def __call__(self, *args, **kwargs):
        datetime = timestamp_to_datetime(self.time)
        it = Simulation().iteration
        Logger().table_log(
            it, datetime, self.name, str(self.entity), self.extra_info())

        return self.function(self.entity, *args, **kwargs)

    @property
    def time(self):
        return self.updated_time(self.entity)

    def update_time(self, new_time):
        if callable(new_time):
            self.updated_time = new_time
        else:
            self.updated_time = lambda p: new_time

    def __repr__(self):
        s = "Event({}, {}, {})"
        return s.format(self.name, self.time, self.entity)


def schedule_initial_events():
    from events.client_events import schedule_arrivals
    from events.external_events import schedule_external_events
    from events.park_events import schedule_initial_park_events

    schedule_arrivals()
    schedule_external_events()
    schedule_initial_park_events()
