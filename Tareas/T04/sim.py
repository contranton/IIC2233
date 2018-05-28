import bisect
from misc_lib import (Singleton, timestamp_to_datetime,
                      timestamp_to_time, Logger)

from params import PARK_CLOSE_TIME


class Scheduler(metaclass=Singleton):
    def __init__(self):
        """
        Manages discrete event scheduling.
        """
        self.reset()

    def reset(self):
        self.event_list = []
        self._event_times = []
        self.time = 0
        self.conditionals = []
        self.obsoletable = {}

    def __call__(self, *args, **kwargs):
        """
        Utility to quickly call self.schedule
        """
        self.schedule(*args, **kwargs)

    def next_event(self):
        """
        Return next timed event
        """
        event = self.event_list.pop(0)
        self._event_times.pop(0)

        # Event has ocurred and is no longer obsoletable
        if event in self.obsoletable:
            self.obsoletable.pop(event)

        return event

    def next_simultaneous_events(self):
        """
        Gets all events that ocurr at the same earliest time
        """
        self.time = self.event_list[0].time
        index = bisect.bisect(self._event_times, self._event_times[0])

        return (self.next_event() for i in range(index))

    def schedule(self, event, time=None, delta=None,
                 obsolete_if=None, condition=None,
                 on_open_hours=False):
        """
        Event scheduler. Can schedule in three different ways:
        1) time  (Time): Defines the absolute time at which event must ocurr
        2) delta (Time): Defines a positive time difference at which
                         event ocurrs
        3) condition (Callable): Event is executed only
                                 when condition() returns True

        The callable obsolete_if parameter will cancel the given event if
        it evaluates to True.

        on_open_hours ensures the delta used lands inside the park's
        opening hours for the day
        """

        sched_time = self.time
        if time:
            if delta:
                raise Exception("Invalid Scheduling. Can't define "
                                "both a 'time' and a 'delta'")
            sched_time = time
        elif delta:
            if on_open_hours:
                delta = self.valid_time(delta)
            sched_time = self.time + delta

        if sched_time > self.max_time:
            print("WARNING: Tried to schedule event {} at time {} which is "
                  "past the maximum time {}. Ignoring.".format(
                      event, sched_time, self.max_time))
            return

        # Conditional events don't depend on time until they're run
        if condition:
            self.conditionals.append((event, condition))
            return

        # Time-dependent events
        event.update_time(sched_time)
        index = bisect.bisect(self._event_times, event.time)
        self.event_list.insert(index, event)
        self._event_times.insert(index, event.time)

        if obsolete_if:
            self.obsoletable[event] = obsolete_if

    def cancel_event(self, event):
        """
        Cancels event after evaluating obsolete_if, hopefully
        """
        # Logger().log("{} was cancelled".format(event))
        self.obsoletable.pop(event)
        index = self.event_list.index(event)
        self.event_list.pop(index)
        self._event_times.pop(index)

    def execute_conditional(self, event, cond):
        """
        Runs the conditional event, updating its time and removing it from
        the event ledger
        """
        event.update_time(self.time)
        event()
        self.conditionals.remove((event, cond))

    @property
    def max_time(self):
        """
        Maximum timestamp time due to only simulating one week
        """
        return 6*60*24 + 23*60 + 59

    @property
    def time_string(self):
        """
        Formatted string containing date and time
        """
        return timestamp_to_datetime(self.time)

    def valid_time(self, delta):
        """
        Bounds a time delta value to the closing time of the park. Impedes
        that in the 10 minutes that a person spends deciding what to do
        they stay over closing hours.
        """
        time_until_close = (PARK_CLOSE_TIME.time() -
                            Simulation().time.time())

        if time_until_close < delta:
            delta = time_until_close
        return delta


class Simulation(metaclass=Singleton):
    def __init__(self):
        self.schedule = Scheduler()
        self.iteration = 0

    def run(self, max_iterations, event_creator):
        """
        Runs the scheduled events until exhaustion.
        Repeats for max_iterations number of times
        """
        while self.iteration < max_iterations:
            self.iteration += 1

            event_creator()
            while self.schedule.event_list:
                # Discard obsolete events
                for event, cond in list(self.schedule.obsoletable.items()):
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
            self.schedule.reset()

    @property
    def time(self):
        return timestamp_to_time(self.schedule.time)
