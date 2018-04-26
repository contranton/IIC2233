"""
-- decoradores.py --

Escriba, en este archivo, todos sus decoradores.
"""

from functools import wraps
from time import time

FILENAME = 'registro.txt'


def write_registro(data):
    with open(FILENAME, 'a') as f:
        f.write(",".join([str(i) for i in data]) + "\n")


def registro(foo):
    @wraps(foo)
    def _(*args, **kwargs):
        name = foo.__name__

        # Combine args with kwargs
        all_args = list(args) + list(kwargs.values())
        str_args = [str(i) for i in all_args]

        result = foo(*args, **kwargs)
        write_registro((name, str_args, result))
        return result
    return _


def verificar_tipos(*types):
    """
    ONLY WELL DEFINED FOR METHODS INSIDE CLASSES
    """
    def inner_dec(foo):
        def _(*args, **kwargs):
            if len(types) != (len(args) + len(kwargs) - 1):
                raise TypeError("La cantidad de argumentos de la "
                                "funcion no coincide con la cantidad "
                                "de argumentos entregados")
            all_args = list(args[1:])+list(kwargs.values())
            for i, (type_, arg) in enumerate(zip(types, all_args)):
                if type(arg) != type_:
                    raise TypeError("El argumento {} no es del tipo {}"
                                    .format(i, type_.__name__))
            result = foo(*args, **kwargs)
            return result
        return _
    return inner_dec


def invertir_string(foo):
    def _(*args, **kwargs):
        results = foo(*args, **kwargs)
        return [s[::-1] for s in results]
    return _


def temporizador(max_time=3):
    def inner(foo):
        @wraps(foo)
        def _(*args, **kwargs):
            time1 = time()
            result = foo(*args, **kwargs)
            tdiff = time() - time1
            if tdiff > max_time:
                print("Funcion excede tiempo esperado:\n"
                      "\tFuncion: {}\n\tTimepo esperado: {}"
                      "\n\tTiempo actual: {}\n"
                      .format(foo.__name__, max_time, tdiff))
            return result
        return _
    return inner


if __name__ == '__main__':
    @verificar_tipos(int, str, str)
    def test(val, name, name2):
        print(val**2)
        print(name)
        print(name2)
