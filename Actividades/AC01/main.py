from personas import Alumno, Profesor, Ayudante


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
        profesores.append(Profesor(nombre="Nebil %i" % i,
                                   nacimiento=date(sample(range_year, 1)[0]-30, 5, 3),
                                   rut=sample(range_rut, 1)[0] - 6*10**6,
                                   seccion=1,
                                   min_val=10,
                                   max_val=25))
        ayudantes.append(Ayudante(nombre="Diego %i" % i,
                                  nacimiento=date(sample(range_year, 1)[0]-5, 5, 3),
                                  rut=sample(range_rut, 1)[0],
                                  seccion=1,
                                  min_val=5,
                                  max_val=15))

    
