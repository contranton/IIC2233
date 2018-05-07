from itertools import tee
from functools import wraps
from library.exceptions import MovieError


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
                            for attr in attrs
                            if getattr(movie, attr) == "N/A"), None)
            if invalid:
                raise MovieError(foo.__name__, invalid[0].title, invalid[1])
            return foo(it2, *args, **kwargs)
        return _
    return dec
