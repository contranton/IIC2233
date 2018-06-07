import os
import json
import pickle
from random import sample


ESTILO = (("label_principal", "background-image: url(gui/logo.png);"),
          ("boton_serializar", "background-image: url(gui/guantlet.png);"),
          ("boton_deserializar", "background-image: url(gui/dragon_balls.png);"),
          ("label_personas","background-color: rgba(30, 232, 204, 153);"),
          ("centralwidget", "#centralwidget{background-color: "
                            "qlineargradient(spread:repeat, x1:0,"
                            " y1:0,x2:1,y2:0,stop:0.197044 "
                            "rgba(179, 179, 179, 255), "
                            "stop:0.64532 rgba(204, 204, 204, 255), "
                            "stop:1 rgba(255, 255, 255, 255));}"),
          ("label_barra", "background-color: rgb(76, 76, 76);"),
          ("scrollArea", "#area{border: 3px solid black;} "
                         "QLabel{border: 1px solid grey; font-weight: bold}"))

class Persona():

    def __init__(self, nombre, apellido_paterno, apellido_materno, numero_alumno,
                 codigo_genetico, hermosura, inteligencia, velocidad):
        self.nombre = nombre
        self.apellido_paterno = apellido_paterno
        self.apellido_materno = apellido_materno
        self.numero_alumno = numero_alumno
        self.codigo_genetico = codigo_genetico
        self.hermosura = hermosura
        self.inteligencia = inteligencia
        self.velocidad = velocidad
        self.serializado = False

        self.ultimas_palabras = ""


    def __getstate__(self):
        ## rellenar método##
        #:return: dict
        self.ultimas_palabras = "Waaa mis referencias a infinity war"\
                                " no me ayudaron a mantenerme vivo"
        return self.__dict__

    def __setstate__(self, state):
        ## rellenar método##
        #:state: dict
        self.ultimas_palabras = ""
        self.__dict__ = state


#################################
#Espacio para JSONEncoder

class PersonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Persona):
            return {"Nombre": obj.nombre,
                    "Apellido": obj.apellido_materno,
                    "Numero de Alumno": obj.numero_alumno}
        else:
            return super().default(obj)

#FUNCIONES
##############################################################################


def person_hook(obj):
    with open("caracteristicas.json", 'r') as file:
        chars = json.load(file)
    out_dict = {}
    for attr in obj:
        if attr in chars:
            out_dict[attr] = obj[attr]
    return Persona(**out_dict)

# Aca hay espacio para una funcion auxiliar, por ejemplo para algun object_hook

def agregar_estilo():
    """
    Retorna el estilo de la interfaz en formato json
    :return: str (formato json)
    """
    obj = {widg: st for widg, st in ESTILO}
    return json.dumps(obj)


def cargar_personas():
    """
    Lee el archivo personas.json, deserializa cada persona en formato json y
    retorna una lista de Personas
    :return: list
    """
    with open("personas.json", 'r') as file:
        personas = json.load(file, object_hook=person_hook)
    return personas


def generar_personas(personas):
    """
    Crea la carpeta Personas que contiene a las personas serializadas con json
    :personas: lista de Personas
    """
    if not os.path.exists("Personas"):
        os.mkdir("Personas")

    for persona in personas:
        with open(f"Personas/{persona.codigo_genetico}.json", 'w') as file:
            json.dump(persona, file, cls=PersonEncoder)


def serializar_personas(personas):
    """
    Crea la carpeta Serializados que contiene a las personas serializadas con pickle
    :personas: lista de Personas
    """
    # Select the lucky ones
    chosen = sample(personas, len(personas)//2)

    if not os.path.exists("Serializados"):
        os.mkdir("Serializados")

    # Write files
    for person in chosen:
        with open(f"Serializados/{person.numero_alumno}.rip", 'wb') as file:
            pickle.dump(person, file)

##############################################################################
