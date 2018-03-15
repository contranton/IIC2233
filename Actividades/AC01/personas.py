from random import randrange, sample
from datetime import date

class Persona(object):
    """Una persona con atributos propios

    """
    def __init__(self, nombre, nacimiento, rut):
        self.nombre = nombre
        self.nacimiento = nacimiento
        self.rut = rut
        
        
class Ensenador(object):
    """Objeto capaz de ensenar

    """
    def __init__(self, min_val, max_val):
        self.min_val = min_val
        self.max_val = max_val

    def ensenar(self, alumno):
        alumno.conocimiento += randrange(self.min_val, self.max_val)
        
class Profesor(Persona, Ensenador):
    """Profesor del curso

    """
    def __init__(self, **kwargs):
        super(Profesor, self).__init__(**kwargs)
        self.seccion = seccion

class Ayudante(Persona, Ensenador):
    """Ayudante del curso

    """
    def __init__(self, conocimiento, **kwargs):
        super(Ayudante, self).__init__(**kwargs)
        self.args = args

class Alumno(Persona):
    """Alumno, capaz de ser ensenado

    """
    def __init__(self, conocimiento=10, ramos):
        super(Alumno, self).__init__()
        self.conocimiento = conocimiento
        self.ramos = ramos
        
        


if __name__ == '__main__':

    # Poblar el sistema proceduralmente
    
    range_rut = (190000000, 200000000)
    range_year = (1960, 2000)
    lista_ramos = ("IIC2233", "IEE2183", "ING1024")

    alumnos = []
    profesores = []
    ayudantes = []
    for i in range(2):
        alumnos.append(Alumno(nombre="Juan %i" % i,
                              nacimiento=date(sample(range_year, 1)[0], 5, 3),
                              rut=sample(range_rut, 1)[0],
                              ramos=lista_ramos))
