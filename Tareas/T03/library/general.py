from typing import Generator, List
from library.tools import with_valid_movie_attrs

from library.getters import (get_rating, get_unique_movie_users,
                             get_top_movies, get_profit, get_movies_from_actor,
                             get_total_profit, get_all_ratings)


@with_valid_movie_attrs("rating_IMDb", "rating_RT", "rating_MC")
def popular_genre(movies: Generator, r_type: str="All") -> List[str]:
    """
    Returns the four best genres according to r_type
    """
    movies = list(movies)
    genres = get_unique_movie_users(movies, "genres")

    gr_ratings = ((genre, sum(map(lambda m: get_rating(m, r_type), movies)))
                  for genre, movies in genres)
    if r_type == "All":
        # If all three ratings are considered, make this the average
        gr_ratings = ((genre, rating/3) for genre, rating in gr_ratings)

    ratings = list(map(lambda x: x[0],
                       sorted(gr_ratings, key=lambda x: x[1])))

    return ratings[-4:][::-1]


@with_valid_movie_attrs("rating_IMDb", "rating_RT", "rating_MC")
def popular_actors(movies: Generator, k_actors: int,
                   n_movies: int, r_type: str="All") -> List[str]:
    """
    Returns the k actors most repeated among movies according to r_type
    """
    movies_list = get_top_movies(movies, r_type)[:n_movies]
    actors = get_unique_movie_users(movies_list, "actors", movies_list)
    return list(
        map(lambda x: x[0],
            sorted(actors, key=lambda x: len(x[1])))
    )[-k_actors:][::-1]


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


@with_valid_movie_attrs("rating_IMDb", "rating_RT", "rating_MC")
def successful_actors(movies: Generator) -> List[str]:
    """
    Returns actors whose every movie has *all* ratings above 50%
    """
    movs = list(movies)
    actors = get_unique_movie_users(movs, "actors")

    result = filter(lambda a:
                    every_movie_rated_above(a[1],
                                            threshold=50),
                    actors)

    return list(map(lambda r: (r[0],
                               list(map(lambda x: x.title, r[1]))), result))


def every_movie_rated_above(movies, threshold):
    """
    Returns a bool stating whether every movie in movies has
    every rating above the threshold
    """
    if not movies:
        return False
    return all(map(lambda movie: all(map(lambda r: r > threshold,
                                         get_all_ratings(movie))),
                   movies))
