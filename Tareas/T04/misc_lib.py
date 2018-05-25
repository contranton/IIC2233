from collections import namedtuple


class Singleton(type):
    instance = None

    def __call__(self, *args, **kwargs):
        if not self.instance:
            self.instance = super().__call__(*args, **kwargs)
        return self.instance


class Logger(metaclass=Singleton):
    pass


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


def timestamp_to_time(timestamp):
    n_day = timestamp // (60*24)
    n_time = timestamp - n_day * (60*24)
    n_hour = n_time // 60
    n_minutes = n_time - n_hour * 60
    return time_nt(n_day, n_hour, n_minutes)


def timestamp_to_datetime(timestamp):
    t = timestamp_to_time(timestamp)
    day = _day_map[t.day]
    return "{:<10}@ {:0>2}:{:0>2}".format(day, t.hour, t.minute)
