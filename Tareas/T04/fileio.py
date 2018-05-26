import csv
from collections import namedtuple


def read_csv(path):
    with open(path, 'r', encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=",")
        return list(reader)


def get_arrivals():
    rows = read_csv("data/arrivals.csv")
    arrival = namedtuple("Arrival", " ".join(rows[0]))
    for day, time, budget, children in rows[1:]:
        yield arrival(day, time, int(budget), int(children))


def get_associations():
    rows = read_csv("data/associations.csv")
    assoc = namedtuple("Association", " ".join(rows[0]))
    for rest, attr in rows[1:]:
        yield assoc(rest, attr)


def get_attractions():
    from entity import Attraction
    rows = read_csv("data/attractions.csv")
    return (Attraction(*row) for row in rows[1:])


def get_restaurants():
    from entity import Restaurant
    rows = read_csv("data/restaurants.csv")
    return (Restaurant(*row) for row in rows[1:])
