import csv
from collections import namedtuple

from entity import Attraction, Restaurant


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
    rows = read_csv("data/attractions.csv")
    attraction = namedtuple("Attraction", " ".join(rows[0]))
    for row in rows[1:]:
        yield Attraction(*row)


def get_restaurants():
    rows = read_csv("data/restaurants.csv")
    restaurant = namedtuple("Restaurant", " ".join(rows[0]))
    for row in rows[1:]:
        yield Restaurant(*row)
