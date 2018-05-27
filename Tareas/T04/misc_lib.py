from collections import namedtuple, deque


class Singleton(type):
    instance = None

    def __call__(self, *args, **kwargs):
        if not self.instance:
            self.instance = super().__call__(*args, **kwargs)
        return self.instance


class Logger(metaclass=Singleton):
    """Data class that aggregates the different statistics required by
    the simulationn
    """
    all_clients = []
    all_rides = []
    school_day_profits = []
    people_left_due_to_events = []

    num_left_by_lack_of_energy = 0
    num_ruziland_failures = 0
    num_people_couldnt_eat = 0

    message_list = deque()

    PRINT = False

    __format = "{:<10} | {:<20} | {:<40} | {:<30} | {}"

    def __init__(self):
        s = "{0}\n{1:^150}\n{0}\n".format("="*150, "N E B I L A N D")
        self.log(s)
        self.table_log("Iteration", "Datetime",
                       "Event", "Entity Affected", "Extra Info")
        self.log("-"*150)

    def table_log(self, iteration, dt, name, entity, extra):
        s = self.__format.format(iteration, dt, name, entity, extra)
        self.log(s)

    def log(self, string):
        if self.PRINT:
            print(string)
        self.message_list.append(string)

    def write(self):
        with open("log.txt", 'w') as f:
            for message in self.message_list:
                f.write(message + "\n")
        


_day_map = ["Lunes", "Martes", "Miercoles",
            "Jueves", "Viernes", "Sábado", "Domingo"]


def datetime_to_time(day, time):
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


time_nt = namedtuple("Time", "day hour minute")
time_nt.raw = lambda t: t.day*60*24 + t.hour*60 + t.minute


def timestamp_to_time(timestamp):
    n_day = timestamp // (60*24)
    n_time = timestamp - n_day * (60*24)
    n_hour = n_time // 60
    n_minutes = n_time - n_hour * 60
    return time_nt(n_day, n_hour, n_minutes)


def timestamp_to_datetime(timestamp):
    t = timestamp_to_time(timestamp)
    try:
        day = _day_map[t.day]
    except:
        print("ERROR: A given date is way invalid. Check it out")
        import pdb; pdb.set_trace()
    return "{:<10}@ {:0>2}:{:0>2}".format(day, t.hour, t.minute)
