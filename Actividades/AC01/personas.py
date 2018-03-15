from random import randrange, sample
import datetime

class Persona(object):
    """Una persona con atributos propios

    """
    def __init__(self, nombre, nacimiento, rut, **kwargs):
        self.nombre = nombre
        self.nacimiento = nacimiento
        self.rut = rut

    @property
    def edad(self):
        t_now = datetime.datetime.now()
        return (t_now.date() - self.nacimiento)

    def __str__(self):
        s = " ".join([self.nombre, str(self.edad)])
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
        super().__init__(min_val=10, max_val=25, **kwargs)
        self.seccion = seccion

    def __str__(self):
        s = super().__str__()
        s += "\nNumero Seccion: %i" % self.seccion
        return s

class Alumno(Persona):
    """Alumno, capaz de ser ensenado

    """
    def __init__(self, conocimiento=10, ramos=[], **kwargs):
        self.conocimiento = conocimiento
        self.ramos = ramos
        super(Alumno, self).__init__(**kwargs)
        

    def estudiar(self):
        self.conocimiento += randrange(5, 10)

    def __str__(self):
        s = super().__str__()
        s += "\nRamos: " + str(self.ramos)
        s += "\nNivel de Conocimiento: %i" % self.conocimiento
        return s

    @property
    def conocimiento(self):
        return self._conocimiento

    @conocimiento.setter
    def conocimiento(self, new):
        self._conocimiento = min(max(100, new), 1)
        if self._conocimiento <= 60:
            print("Si sigo asi, me voy a echar el ramo D:")
        else:
            print("Que chevere Python! Voy a postular a TPD para aprender mas.")


class Ayudante(Alumno, Ensenador):
    """Ayudante del curso

    """
    def __init__(self, seccion, **kwargs):
        super().__init__(min_val=5, max_val=15, **kwargs)
        self.seccion = seccion


