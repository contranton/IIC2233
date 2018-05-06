from typing import Generator, List, Callable
from itertools import takewhile, tee
from functools import wraps
from collections import namedtuple

from fileio import read_csv
from preproc import is_bot, clean_html
from exceptions import BadQuery, WrongInput, MovieError

ops = {"==": lambda x, y: x == y,
       "!=": lambda x, y: x != y,
       ">": lambda x, y: x > y,
       "<": lambda x, y: x < y}


movie_nt = namedtuple("Movie", "id title rating_IMDb "
                      "rating_RT rating_MC box_office date")


DB = "MiniDatabase/"
#DB = "Database/"

# Helper functions


def with_valid_movie_attrs(*attrs):
    """
    Decorator that checks that some function that uses a movies generator
    has all attributes used in the function. Else, raises MovieError.
    """
    def dec(foo):
        @wraps(foo)
        def _(movies, *args, **kwargs):
            it1, it2 = tee(movies)
            get_attrs = lambda m: (getattr(m, attr) for attr in attrs)
            invalid = next(((movie, attr) for movie in it1
                            for attr in get_attrs(movie)
                            if attr == "N/A"), None)
            if invalid:
                raise MovieError(foo.__name__, invalid[0], invalid[1])
            return foo(it2, *args, **kwargs)
        return _
    return dec


# Database-loading functions


def read_reviews():
    return map(
        lambda r: clean_html(r[1]),
        filter(lambda r: not is_bot(r[1]),
               read_csv(DB + "reviews.csv"))
    )


def load_database(test=False) -> Generator:
    """
    Return movies present in 'movies.csv'
    """
    db = "MiniDatabase/" if test else "Database/"
    return (movie_nt(*m) for m in read_csv(db + "movies.csv"))


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


def get_movie_reviews(movie):
    return filter(lambda x: x[0] == movie.id,
                  read_csv(DB + "reviews.csv"))


def best_comments(movies: Generator, n: int) -> Generator:
    """
    Finds top 'n' movies with most positive coments.

    If n < 0, returns the top |n| most negatively commented movies.
    """
    comments = ((movie, sum(map(lambda c: get_review_positivity(c[1]),
                                get_movie_reviews(movie))))
                for movie in movies)
    comments = list(sorted(comments, key=lambda x: x[1]))
    best_movies = list(map(lambda x: x[0], comments))
    return best_movies[-n:] if n > 0 else best_movies[:-n]


def get_top_movies(movies, r_type="All"):
    return sorted(movies, key=lambda m: get_rating(m, r_type))


def take_fully_defined_movies(movies, raise_error=False):
    """
    Only gets movies with every attribute distinct from N/A
    """
    for movie in movies:
        if not any((getattr(movie, attr) == "N/A"
                    for attr in movie._fields)):
            yield movie
        elif raise_error:
            raise MovieError()


def take_movie_while(movies: Generator, column: str,
                     symbol: str, value: int) -> Generator:
    """
    Returns movies whose attribute in 'column' statisfies the
    conditions specified by 'symbol' and 'value'.
    """

    # What a pretty hack :'D
    # Ensures movies have the desired attribute
    @with_valid_movie_attrs(column)
    def check(movies): pass
    check(movies)

    if column not in movie_nt._fields:
        raise WrongInput("take_movie_while", "column", column)
    op = ops[symbol]
    if column not in "id title box_office date".split(" "):
        attr = lambda m: get_rating(m, column.split("_")[-1])
    else:
        attr = lambda m: getattr(m, column)
    return takewhile(lambda m: op(attr(m), value), movies)


# Non Database-returning functions

def get_rating(movie, r_type="All"):
    try:
        res = []
        if r_type in ("All", "IMDb", "Internet Movie Database"):
            res += [int(movie.rating_IMDb.split("/")[0].replace(".", ""))]
        elif r_type in ("All", "MC", "Metacritic"):
            res += [int(movie.rating_MC.split("/")[0])]
        elif r_type in ("All", "RT", "Rotten Tomatoes"):
            res += [int(movie.rating_RT[:-1])]
        else:
            raise BadQuery()
        return sum(res)
    except ValueError:
        raise MovieError()


def get_movies_from_genre(movies, genre):
    movies = map(lambda act: act[0],  # Movie ID
                 filter(lambda x: x[1] == genre, read_csv(DB + "genres.csv")))
    movies = filter(lambda m: m.id == id, movies)
    return movies


@with_valid_movie_attrs("rating_IMDb", "rating_RT", "rating_MC")
def popular_genre(movies: Generator, r_type: str="All") -> List[str]:
    """
    Returns the four best genres according to r_type
    """
    movies = list(movies)
    genres = get_unique_movie_users(movies, "genres", movies)
    gr_mvs = ((genre, map(lambda id: get_movie_from_id(movies, id), ids))
              for genre, ids in genres)
    gr_ratings = ((genre, sum(map(lambda m: get_rating(m, r_type), movies)))
                  for genre, movies in gr_mvs)
    if r_type == "All":
        # If all three ratings are considered, make this the average
        gr_ratings = ((genre, rating/3) for genre, rating in gr_ratings)

    ratings = list(map(lambda x: x[0],
                       sorted(gr_ratings, key=lambda x: x[1])))

    return ratings[:4]


@with_valid_movie_attrs("rating_IMDb", "rating_RT", "rating_MC")
def popular_actors(movies: Generator, k_actors: int,
                   n_movies: int, r_type: str="All") -> List[str]:
    """
    Returns the k actors most repeated among movies according to r_type
    """
    movies_list = get_top_movies(movies, r_type)[:n_movies]
    actors = get_unique_movie_users(movies_list, "actors", movies_list)
    return list(
        map(lambda x: x.item,
            sorted(actors, key=lambda x: len(x.ids)))
    )[-k_actors:][::-1]


def get_movie_from_id(movies, id):
    movies, mov2 = tee(movies)
    return next(filter(lambda m: m.id == id, movies))


def get_movies_from_actor(movies, actor):
    movies = map(lambda act: act[0],  # Movie ID
                 filter(lambda x: x[1] == actor, read_csv(DB + "actors.csv")))
    movies = filter(lambda m: m == id, movies)
    return list(movies)


def get_biased_word_percentages(words_list):
    L = len(words_list)
    words = list(filter(lambda x: x[0].lower() in words_list,
                        read_csv("words.csv")))

    positives = len(list(filter(lambda x: x[1] == "positive", words)))
    negatives = len(list(filter(lambda x: x[1] == "negative", words)))
    # TODO: Change this back to the default behavior
    # As it is, it takes the percentage only among biased words, not all
    L2 = positives + negatives
    L2 = L2 if L2 != 0 else 1
    return (positives/L2, negatives/L2)


def get_review_positivity(review):
    """
    Returns "+" if positive, "-" if negative, "o" if neutral
    """
    words = review.split(" ")
    per_P, per_N = get_biased_word_percentages(words)

    if per_P > 0.6 or (per_P > 0.4 and per_N < 0.2):
        return 1
    if per_N > 0.6 or(per_N > 0.4 and per_P < 0.2):
        return -1
    return 0


def get_profit(movie):
    L = len(list(filter(lambda act: act[0] == movie,
                        read_csv(DB + "actors.csv"))))
    return movie.box_office / L


item_ids = namedtuple("item_ids", "item ids")


def get_unique_movie_users(movies, type_, movies_list=None) -> Generator:
    """
    Returns every item paired with all movies it's associated with.
    If movies_list is given, items are limited to those movies, else
    all movies are considered

    type_ is either 'actors' or 'genres'
    """
    path = DB + "/" + type_ + ".csv"
    uniques = set()
    movie_list_ids = lambda: map(lambda m: m.id, movies_list)
    for id, item in read_csv(path):
        if item not in uniques:
            # If movies-list has been given but item isn't in it, skip it
            if movies_list and id not in movie_list_ids():
                continue
            uniques.add(item)
            # Get all movie ids associated with item
            ids = map(lambda x: x[0],
                      filter(lambda x: x[1] == item, read_csv(path)))
            if movies_list:
                ids = filter(lambda i: i in movie_list_ids(), ids)
            assoc_movs = map(lambda i: get_movie_from_id(movies, i), ids)
            yield (item, list(assoc_movs))


def get_total_profit(movies):
    return sum((get_profit(movie) for movie in movies))


@with_valid_movie_attrs("box_office")
def highest_paid_actors(movies: Generator, k_actors: int=1) -> List[str]:
    """
    Returns the k best-paid actors

    TODO: getmoviesfromactor is redundant since we have the ids
    This is the only place we care about profit. Use reduce!
    """
    movies = list(movies)
    actors = get_unique_movie_users(movies, "actors")
    actor_movies = ((actor, get_movies_from_actor(movies, actor))
                    for actor, movies in actors)
    actor_pays = ((actor,
                   get_total_profit(movies),
                   sorted(list(movies), key=lambda m: get_profit(m)))
                  for actor, movies in actor_movies)

    return list(actor_pays)[:k_actors]


def get_all_ratings(movie):
    return [get_rating(movie, "IMDb"),
            get_rating(movie, "RT"),
            get_rating(movie, "MC")]


def every_movie_rated_above(movies, threshold):
    """
    Returns a bool stating whether every movie in movies has
    every rating above the threshold
    """
    return all(map(lambda movie: all(map(lambda r: r > threshold,
                                         get_all_ratings(movie))),
                   movies))


@with_valid_movie_attrs("rating_IMDb", "rating_RT", "rating_MC")
def successful_actors(movies: Generator) -> List[str]:
    """
    Returns actors whose every movie has *all* ratings above 50%
    """
    movies = list(movies)
    actors = get_unique_movie_users(movies, "actors")

    result = filter(lambda a:
                    every_movie_rated_above(a[1],
                                            threshold=50),
                    actors)

    return list(result)


__foos__ = {
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
        return __foos__[name]
    except KeyError:
        raise BadQuery(name)

    
def run_query(args):
    foo = args[0]
    args = map(lambda arg: run_query(arg) if isinstance(arg, list) else arg,
               args[1:])
    return get_function_from_name(foo)(*args)


if __name__ == '__main__':
    get_movies = lambda: take_fully_defined_movies(load_database(True))
