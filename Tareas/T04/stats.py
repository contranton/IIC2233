from collections import namedtuple
from misc_lib import Logger


def mean(data, key=lambda x: x):
    """
    Returns the mean of the given data.

    Key modifies the list if desired
    """
    L = len(data)
    return sum(map(key, data), key=key)/L


statistic = namedtuple("Statistic", "name value")


def get_average_waiting_time():
    return statistic(
        "Tiempo promedio de espera en fila",
        mean([client.avg_waiting_time for client in Logger().all_clients])
    )


def get_average_cries():
    return [
        statistic(
            "Promedio de llantos por atraccion",
            statistic(ride.name,
                      ride.average_cries))
        for ride in Logger().all_rides]


def total_people_leave_energy():
    return statistic(
        "Total de personas que se van del parque por falta de energia",
        Logger().num_left_by_lack_of_energy
    )


def average_remaining_energy():
    return statistic(
        "Energia promedio de personas al salir del parque",
        mean([client.energy_at_exit for client in Logger().all_clients])
    )


def profit_in_school_days():
    return statistic(
        "Total de dinero recaudado en dias de colegio",
        sum(Logger().school_day_profits)
    )


def failures_due_to_invasion():
    # Add counter whenever that 40% or something is true
    return statistic(
        "Total de fallas causadas por Ruziland",
        Logger().num_ruziland_failures
    )


def ride_with_most_failures():
    return statistic(
        "Atraccion con mayor cantidad de fallas",
        max(lambda x: x.total_failures, Logger().all_rides)
    )


def total_people_who_couldnt_eat():
    return statistic(
        "Total de personas que no pudieron comer en restaurantes",
        Logger().num_people_couldnt_eat
    )


def average_time_in_restaurant():
    return statistic(
        "Tiempo promedio en un restaurante",
        mean([mean(client.time_in_restaurants)
              for client in Logger().all_clients])
    )


def max_time_ride_broken():
    return statistic(
        "Tiempo maximo de atraccion Fuera de Servicio",
        max([max(ride.times_spent_broken) for ride in Logger().all_rides])
    )


def average_access_wasted_time():
    pass


def average_calls_to_clean():
    return statistic(
        "Promedio de llamados a hacer aseo",
        None
    )


def average_calls_to_fix():
    return statistic(
        "Promedio de llamados a hacer reparaciones",
        None
    )


def profit_lost_due_to_events():
    return statistic(
        "Dinero perdido en entradas debido a eventos externos",
        sum(map(lambda p: p.budget, Logger().people_left_due_to_events))
    )


def total_money_not_spent():
    return statistic(
        "Dinero total no gastado por visitantes",
        sum(map(lambda c: c.unspent_budget, Logger().all_clients))
    )
