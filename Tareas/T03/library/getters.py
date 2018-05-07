from typing import Generator
from itertools import tee

import library as L
from library.fileio import read_csv
from library.exceptions import BadQuery, MovieError


def get_movie_reviews(movie):
    return filter(lambda x: x[0] == movie.id,
                  read_csv(L.DB + "reviews.csv"))


def get_top_movies(movies, r_type="All"):
    return sorted(movies, key=lambda m: get_rating(m, r_type))


def get_rating_attr(rating):
    if rating in ("IMDb", "Internet Movie Database"):
        return "rating_IMDb"
    elif rating in ("MC", "Metacritic"):
        return "rating_MC"
    elif rating in ("RT", "Rotten Tomatoes"):
        return "rating_RT"
    return None


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
                 filter(lambda x: x[1] == genre, read_csv(L.DB + "genres.csv")))
    movies = filter(lambda m: m.id == id, movies)
    return movies


def get_movie_from_id(movies, id):
    movies, mov2 = tee(movies)
    return next(filter(lambda m: m.id == id, mov2))


def get_movies_from_actor(movies, actor):
    movs = map(lambda act: act[0],  # Movie ID
               filter(lambda x: x[1] == actor, read_csv(L.DB + "actors.csv")))
    movs = (get_movie_from_id(movies, id) for id in movs)
    return list(movs)


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
    Returns 1 if positive, -1 if negative, 0 if neutral
    """
    words = review.split(" ")
    per_P, per_N = get_biased_word_percentages(words)

    if per_P > 0.6 or (per_P > 0.4 and per_N < 0.2):
        return 1
    if per_N > 0.6 or(per_N > 0.4 and per_P < 0.2):
        return -1
    return 0


def get_profit(movie):
    length = len(list(filter(lambda act: act[0] == movie,
                             read_csv(L.DB + "actors.csv"))))
    bo = int(movie.box_office[1:].replace(".", ""))
    return bo / max(length, 1)


def get_unique_movie_users(movies, type_, movies_list=None) -> Generator:
    """
    Returns every item paired with all movies it's associated with.
    If movies_list is given, items are limited to those movies, else
    all movies are considered

    type_ is either 'actors' or 'genres'
    """
    path = L.DB + "/" + type_ + ".csv"
    print(L.DB)
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


def get_all_ratings(movie):
    return [get_rating(movie, "IMDb"),
            get_rating(movie, "RT"),
            get_rating(movie, "MC")]
