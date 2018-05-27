import bisect
from misc_lib import (Singleton, timestamp_to_datetime,
                      timestamp_to_time, Logger)


class Scheduler(metaclass=Singleton):
    def __init__(self):
        self.event_list = []
        self._event_times = []
        self.time = 0
        self.conditionals = []
        self.obsoletable = []

    def __call__(self, *args, **kwargs):
        self.schedule(*args, **kwargs)

    def next_event(self):
        event = self.event_list.pop(0)
        self._event_times.pop(0)

        return event

    def next_simultaneous_events(self):
        """Gets all events that ocurr at the same earliest time
        """
        self.time = self.event_list[0].time
        index = bisect.bisect(self._event_times, self._event_times[0])

        return (self.next_event() for i in range(index))

    def schedule(self, event, time=None, delta=None,
                 obsolete_if=None, condition=None):
        sched_time = self.time
        if time:
            if delta:
                raise Exception("Invalid Scheduling. Can't define "
                                "both a 'time' and a 'delta'")
            sched_time = time
        elif delta:
            sched_time = self.time + delta

        if sched_time > self.max_time:
            print("WARNING: Tried to schedule event {} at time {} which is "
                  "past the maximum time {}. Ignoring.".format(
                      event, sched_time, self.max_time))
            return

        # Conditional events don't depend on time
        if condition:
            self.conditionals.append((event, condition))
            return

        # Time-dependent events
        event.update_time(sched_time)
        index = bisect.bisect(self._event_times, event.time)
        self.event_list.insert(index, event)
        self._event_times.insert(index, event.time)

        if obsolete_if:
            self.obsoletable.append((event, obsolete_if))

    def cancel_event(self, event):
        # TODO: Log this
        Logger().log("{} was cancelled".format(event))
        self.event_list.remove(event)

    def execute_conditional(self, event, cond):
        event.update_time(self.time)
        event()
        self.conditionals.remove((event, cond))

    @property
    def max_time(self):
        return 7*60*24 + 23*60 + 59

    @property
    def time_string(self):
        return timestamp_to_datetime(self.time)


class Simulation(metaclass=Singleton):
    def __init__(self):
        self.schedule = Scheduler()
        self.iteration = 0

    def run(self):
        while self.schedule.event_list:
            # Discard obsolete events
            for event, cond in self.schedule.obsoletable:
                if cond(event.entity):
                    self.schedule.cancel_event(event)

            # Get all next events that ocurr at the same time
            events = self.schedule.next_simultaneous_events()

            # Execute em
            [event() for event in events]

            # Run conditional events
            for event, cond in self.schedule.conditionals:
                if cond():
                    self.schedule.execute_conditional(event, cond)

    @property
    def time(self):
        return timestamp_to_time(self.schedule.time)
