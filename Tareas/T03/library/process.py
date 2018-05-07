import library.databases as D
import library.general as G

from library.exceptions import BadQuery, WrongInput, MovieError

__foos__ = {
    "filter_by_date": D.filter_by_date,
    "popular_movies": D.popular_movies,
    "best_comments": D.best_comments,
    "take_movie_while": D.take_movie_while,
    "popular_genre": G.popular_genre,
    "popular_actors": G.popular_actors,
    "highest_paid_actors": G.highest_paid_actors,
    "successful_actors": G.successful_actors,
    "load_database": D.load_database,
}


def get_function_from_name(name: str):
    try:
        return __foos__[name]
    except KeyError:
        raise BadQuery(name)


def run_query(args):
    foo = args[0]
    args = map(lambda arg: run_query(arg) if isinstance(arg, list) else arg,
               args[1:])
    return get_function_from_name(foo)(*args)


def process_queries(queries):
    query_num = 1
    results = map(lambda q: (q[0], list(run_query(q))),  queries)
    while results:
        hdr = "-"*10 + "CONSULTA %i" + "-"*10 + "\n"
        text = hdr % (query_num) + "Consulta "
        try:
            result = next(results)
            text += result[0] + ":\n\t"
            text += "\n\t".join((str(i) for i in result[1])) + "\n"
        except (BadQuery, MovieError, WrongInput) as exc:
            text += "Error: " + repr(exc) + "\n"
        yield text
        query_num += 1
