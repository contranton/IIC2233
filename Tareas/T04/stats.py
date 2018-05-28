from misc_lib import Logger


def mean(data, key=lambda x: x):
    """
    Returns the mean of the given data.

    Key modifies the list if desired
    """
    L = max(len(list(data)), 1)
    return sum(map(key, data))/L


class Statistic:
    def __init__(self, name, value):
        """
        Data holder for a statistic, with a name describing it and its
        value
        """
        self.name = name
        self.value = value

    def __repr__(self):
        s = self.value
        if isinstance(s, list):
            s = "\n\t" + "\n\t".join([str(i) for i in s])
        return "{}: {}".format(self.name, s)


def get_average_waiting_time():
    return Statistic(
        "Tiempo promedio de espera en fila",
        mean([client.avg_waiting_time for client in Logger().all_clients])
    )


def get_average_cries():
    return Statistic(
            "Promedio de llantos en atraccion",
            [Statistic(ride.name,
                       mean(ride.cry_num.values()))
             for ride in Logger().all_rides])


def total_people_leave_energy():
    return Statistic(
        "Total de personas que se van del parque por falta de energia",
        Logger().num_left_by_lack_of_energy
    )


def average_remaining_energy():
    return Statistic(
        "Energia promedio de personas al salir del parque",
        mean([client.energy_at_exit for client in
              filter(lambda c: not c.left_due_to_energy,
                     Logger().all_clients)])
    )


def profit_in_school_days():
    raise NotImplementedError()
    # return Statistic(
    #     "Total de dinero recaudado en dias de colegio",
    #     sum(Logger().school_day_profits)
    #)


def failures_due_to_invasion():
    # Add counter whenever that 40% or something is true
    return Statistic(
        "Total de fallas causadas por Ruziland",
        Logger().num_ruziland_failures
    )


def ride_with_most_failures():
    return Statistic(
        "Atraccion con mayor cantidad de fallas",
        max(Logger().all_rides, key=lambda x: x.total_failures)
    )


def total_people_who_couldnt_eat():
    return Statistic(
        "Total de personas que no pudieron comer en restaurantes",
        Logger().num_people_couldnt_eat
    )


def average_time_in_restaurant():
    return Statistic(
        "Tiempo promedio en un restaurante",
        mean([mean(client.times_in_restaurants)
              for client in Logger().all_clients])
    )


def max_time_ride_broken():
    ride = max([ride for ride in Logger().all_rides],
               key=lambda r: max(r.times_spent_broken, default=0))
    return Statistic(
        "Tiempo maximo de atraccion Fuera de Servicio",
        (ride.name, max(ride.times_spent_broken))
    )


def average_access_wasted_time():
    return Statistic(
        "Tiempo promedio perdido en fila",
        mean([mean(client.wasted_times) for client in Logger().all_clients])
    )


def average_calls_to_clean():
    return Statistic(
        "Promedio de llamados a hacer aseo",
        mean(Logger().clean_calls_per_day)
    )


def average_calls_to_fix():
    return Statistic(
        "Promedio de llamados a hacer reparaciones",
        mean(Logger().fix_calls_per_day)
    )


def profit_lost_due_to_events():
    return Statistic(
        "Dinero perdido en entradas debido a eventos externos",
        sum(map(lambda p: p.budget, Logger().people_left_due_to_events))
    )


def total_money_not_spent():
    return Statistic(
        "Dinero total no gastado por visitantes",
        sum(map(lambda c: c.budget, Logger().all_clients))
    )

all_stats = [get_average_waiting_time, get_average_cries,
             total_people_leave_energy, average_remaining_energy,
             failures_due_to_invasion, ride_with_most_failures,
             total_people_who_couldnt_eat, average_time_in_restaurant,
             max_time_ride_broken, average_access_wasted_time,
             average_calls_to_clean, average_calls_to_fix,
             profit_lost_due_to_events, total_money_not_spent]


def run_all_stats():
    for foo in all_stats:
        stat = foo()
        print(stat)
