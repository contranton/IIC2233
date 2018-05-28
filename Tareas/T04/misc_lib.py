from collections import namedtuple, deque
import sys


class Singleton(type):
    """
    Utility metaclass used to access a unique instance of a class from
    anywhere in the code without explicitly passing it as arguments.

    It's basically a glorified 'globals' xd
    """
    instance = None

    def __call__(self, *args, **kwargs):
        """
        Returns the existing unique instance if any, or creates a new one
        before doing so
        """
        if not self.instance:
            self.instance = super().__call__(*args, **kwargs)
        return self.instance


class Logger(metaclass=Singleton):
    """
    Data class that aggregates the different statistics required by
    the simulation and logs messages
    """
    all_clients = []
    all_rides = []
    school_day_profits = []
    people_left_due_to_events = []

    num_left_by_lack_of_energy = 0
    num_ruziland_failures = 0
    num_people_couldnt_eat = 0

    clean_calls_per_day = {i: 0 for i in range(7)}
    fix_calls_per_day = {i: 0 for i in range(7)}

    message_list = deque()

    PRINT = False

    __format = "{:<10} | {:<20} | {:<40} | {:<30} | {}"

    def __init__(self):
        """
        Initializer for logger. Logs some introductory messages
        """
        s = "{0}\n{1:^150}\n{0}\n".format("="*150, "N E B I L A N D")
        self.log(s)
        self.table_log("Iteration", "Datetime",
                       "Event", "Entity Affected", "Extra Info")
        self.log("-"*150)

    def table_log(self, iteration, dt, name, entity, extra):
        """
        Logs the given inputs in tabular form according to the
        specifications
        """
        s = self.__format.format(iteration, dt, name, entity, extra)
        self.log(s)

    def log(self, string):
        """
        Records 'string' to the inner message array
        """
        if self.PRINT:
            print(string)
            sys.stdout.flush()
        self.message_list.append(string)

    def write(self):
        """
        Writes all records to file
        """
        with open("log.txt", 'w') as f:
            for message in self.message_list:
                f.write(message + "\n")


_day_map = ["Lunes", "Martes", "Miercoles",
            "Jueves", "Viernes", "Sábado", "Domingo"]


def datetime_to_time(day, time):
    """
    Converts day and time values to a single integer timestamp.
    Considers a single week only.

    >>> datetime_to_time("Lunes", "15:30")
    930
    """
    try:
        n_day = _day_map.index(day) * 60 * 24
    except KeyError as e:
        raise Exception("Invalid date string '{}'".format(day))
    hour = int(time[:2])
    if hour > 23:
        raise Exception("Invalid hour {}".format(hour))
    minutes = int(time[3:])
    n_time = hour*60 + minutes
    return n_day + n_time


class Time:
    def __init__(self, day, hour, minute):
        """
        Time object used to manage timestamping and time management
        """
        self.day = day
        self.hour = hour
        self.minute = minute

    def raw(self):
        """
        Returns an integer codifying the actual day and time

        Because we only model a week, the effective maximum value is
        90060
        """
        return self.day*60*24 + self.hour*60 + self.minute

    def time(self):
        """
        Returns the equivalent timestamp of only the hour and minutes
        """
        return self.raw() % (60 * 24)

    def day_ts(self):
        """
        Returns the equivalent timestamp of just the day
        """
        return self.raw() // (60 * 24)


def timestamp_to_time(timestamp):
    """
    Turns an integer timestamp to a Time object
    """
    n_day = timestamp // (60*24)
    n_time = timestamp - n_day * (60*24)
    n_hour = n_time // 60
    n_minutes = n_time - n_hour * 60
    return Time(n_day, n_hour, n_minutes)


def timestamp_to_datetime(timestamp):
    t = timestamp_to_time(timestamp)
    try:
        day = _day_map[t.day]
    except:
        print("ERROR: A given date is way invalid. Check it out")
        import pdb; pdb.set_trace()
    return "{:<10}@ {:0>2}:{:0>2}".format(day, t.hour, t.minute)
