import os.path as path

from typing import Generator
from collections import namedtuple
from functools import wraps
from itertools import takewhile

from library.fileio import read_csv
from library.tools import with_valid_movie_attrs
from library import SKIP_NA, DB

from library.getters import (get_rating, get_movie_reviews,
                             get_review_positivity, get_rating_attr)
from library.exceptions import WrongInput

movie_nt = namedtuple("Movie", "id title rating_IMDb "
                      "rating_RT rating_MC box_office date")
movie_nt.__str__ = lambda self: self.title


def load_database(test=False) -> Generator:
    """
    Return movies present in 'movies.csv'
    """
    db = "MiniDatabase/" if test else "Database/"
    movies = (movie_nt(*m) for m in read_csv(db + "movies.csv"))
    if SKIP_NA:
        return take_fully_defined_movies(movies)
    return movies


@with_valid_movie_attrs("date")
def filter_by_date(movies: Generator, date: int,
                   lower: bool=True) -> Generator:
    """
    Takes a movie database and returns the ones older than date if
    'lower' is True or the more recent ones if 'lower' is False.

    """
    return filter(lambda m: (int(m.date) < date) if lower
                  else (int(m.date) > date), movies)


@with_valid_movie_attrs("rating_IMDb", "rating_RT", "rating_MC")
def popular_movies(movies: Generator, r_min: int, r_max: int,
                   r_type: str="All") -> Generator:
    """
    Returns all movies whose ratings are between specified values
    """
    return filter(lambda m: r_min < get_rating(m, r_type) < r_max,
                  movies)


def best_comments(movies: Generator, n: int) -> Generator:
    """
    Finds top 'n' movies with most positive coments.

    If n < 0, returns the top |n| most negatively commented movies.
    """
    comments = ((movie, sum(map(lambda c: get_review_positivity(c[1]),
                                get_movie_reviews(movie))))
                for movie in movies)
    comments = list(sorted(comments, key=lambda x: x[1]))
    best_movies = list(map(lambda x: x[0].title, comments))
    bests = best_movies[-n:] if n > 0 else best_movies[:-n]
    return bests[::-1]


ops = {"==": lambda x, y: x == y,
       "!=": lambda x, y: x != y,
       ">": lambda x, y: x > y,
       "<": lambda x, y: x < y}


def take_movie_while(movies: Generator, column: str,
                     symbol: str, value: int) -> Generator:
    """
    Returns movies whose attribute in 'column' statisfies the
    conditions specified by 'symbol' and 'value'.
    """

    # What a pretty hack :'D
    # Ensures movies have the desired attribute
    foo = wraps(take_movie_while)(lambda m: None)
    attr = get_rating_attr(column)
    attr = attr if attr else column
    with_valid_movie_attrs(attr)(foo)(movies)

    if column not in movie_nt._fields:
        raise WrongInput("take_movie_while", "column", column)
    op = ops[symbol]
    if column not in "id title box_office date".split(" "):
        attr = lambda m: get_rating(m, column.split("_")[-1])
    else:
        attr = lambda m: getattr(m, column)
    return takewhile(lambda m: op(attr(m), value), movies)


def read_reviews():
    name = "reviews.csv"
    if path.exists(DB + "reviews_clean.csv"):
        name = "reviews_clean.csv"
    return read_csv(DB + name)


def take_fully_defined_movies(movies):
    """
    Only gets movies with every attribute distinct from N/A
    """
    for movie in movies:
        if not any((getattr(movie, attr) == "N/A"
                    for attr in movie._fields)):
            yield movie
