class Singleton(type):
    instance = None

    def __call__(self, *args, **kwargs):
        if not self.instance:
            self.instance = super().__call__(*args, **kwargs)
        return self.instance


class Logger(metaclass=Singleton):
    pass


_day_map = {"Lunes": 0, "Martes": 1, "Miercoles": 2,
            "Jueves": 3, "Viernes": 4, "Sábado": 5, "Domingo": 6}


def datetime_to_time(day, time):
    try:
        n_day = _day_map[day] * 60 * 24
    except KeyError as e:
        raise Exception("Invalid date string '{}'".format(day))
    hour = int(time[:2])
    if hour > 23:
        raise Exception("Invalid hour {}".format(hour))
    minutes = int(time[3:])
    n_time = hour*60 + minutes
    return n_day + n_time
