from typing import Generator, List, Callable
from itertools import takewhile
from collections import namedtuple

from fileio import read_file
from preproc import is_bot, clean_html
from exceptions import BadQuery, WrongInput, MovieError

ops = {"==": lambda x, y: x == y,
       "!=": lambda x, y: x != y,
       ">": lambda x, y: x > y,
       "<": lambda x, y: x < y}

rating = namedtuple("Rating", "imdb rt metacritic")
movie = namedtuple("Movie", "title rating box_office date")


## Database-loading functions

def read_reviews():
    return map(
        lambda r: clean_html(r),
        filter(lambda r: not is_bot(r),
               read_file("MiniDatabase/reviews.csv"))
    )

def load_database() -> Generator:
    """
    Return movies present in 'movies.csv'
    """
    return (movie(*m) for m in read_file("MiniDatabase/movies.csv"))


def filter_by_date(movies: Generator, date: int,
                   lower: bool=True) -> Generator:
    """
    Takes a movie database and returns the ones older than date if
    'lower' is True or the more recent ones if 'lower' is False.

    """
    return filter(lambda m: m.date < date if lower else m.date > date,
                  movies)


def popular_movies(movies: Generator, r_min: int, r_max: int,
                   r_type: str="All") -> Generator:
    """
    Returns all movies whose ratings are between specified values
    """
    pass


def best_comments(movie: Generator, n: int) -> Generator:
    """
    Finds top 'n' movies with most positive coments.

    If n < 0, returns the top |n| most negatively commented movies.
    """
    pass
    

def take_movie_while(movies: Generator, column: str,
                     symbol:str, value:int) -> Generator:
    """
    Returns movies whose attribute in 'column' statisfies the
    conditions specified by 'symbol' and 'value'.
    """
    if column not in movie._fields:
        raise BadQuery()
    op = ops[symbol]
    return takewhile(lambda m: op(getattr(m, column), value),
                     movies)


## Non Database-returning functions


def popular_genre(movies: Generator, r_type: str="All") -> List[str]:
    """
    Returns the four best genres according to r_type
    """
    pass


def popular_actors(movies: Generator, k_actors: int,
                   n_movies: int, r_type: str="All") -> List[str]:
    """
    Returns the k actors most repeated among movies according to r_type
    """
    pass


def highest_paid_actors(movies: Generator, k_actors: int=1) -> List[str]:
    """
    Returns the k best-paid actors
    """
    pass

def successful_actors(movies: Generator) -> List[str]:
    """
    Returns actors whose every movie has all ratings above 50%
    """
    pass


_foos = {
    "filter_by_date": filter_by_date,
    "popular_movies": popular_movies,
    "best_comments": best_comments,
    "take_movie_while": take_movie_while,
    "popular_genre": popular_genre,
    "popular_actors": popular_actors,
    "highest_paid_actors": highest_paid_actors,
    "successful_actors": successful_actors,
    "load_database": load_database,
}


def get_function_from_name(name: str) -> Callable:
    try:
        return _foos[name]
    except KeyError:
        raise BadQuery(name)
