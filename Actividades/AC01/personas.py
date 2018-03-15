from random import randrange, sample
import datetime

date = datetime.date
now = datetime.datetime.now

class Persona(object):
    """Una persona con atributos propios

    """
    def __init__(self, nombre, nacimiento, rut):
        self.nombre = nombre
        self.nacimiento = nacimiento
        self.rut = rut

    @property
    def edad(self):
        t_now = now()
        return (t_now() - self.nacimiento).year

    def __str__(self):
        s = " ".join(self.nombre, self.edad)
        return s

    def __repr__(self):
        s = "%s (%i)" % (self.nombre, self.rut)
        return s


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
    def __init__(self, seccion, **kwargs):
        super().__init__(**kwargs)
        self.seccion = seccion

    def __str__(self):
        s = super().__str__()
        s += "\nNumero Seccion: %i" % self.seccion
        return s

class Ayudante(Persona, Ensenador):
    """Ayudante del curso

    """
    def __init__(self, conocimiento=75, **kwargs):
        super().__init__(**kwargs)
        self.conocimiento = conocimiento

class Alumno(Persona):
    """Alumno, capaz de ser ensenado

    """
    def __init__(self, conocimiento=10, ramos=[], **kwargs):
        super().__init__(**kwargs)
        self.conocimiento = conocimiento
        self.ramos = ramos
        

