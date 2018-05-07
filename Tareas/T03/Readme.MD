# Tarea 3 - Javier Contreras

## Consideraciones Generales:
- Todos los archivos distintos a `main.py` deberían estar en el mismo lugar en que se encuentran en el Syllabus. La base de datos MovieDatabase es utilizada por testing, y una variable de modulo `DB` definida en `__init__.py` especifica de cual directorio tomar los datos para consultas generales.
- En library.__init__.py está definida una constante `SKIP_NA`. Si esta es `True`, a la hora de leer las películas se ignorará cualquiera que tenga algún "N/A" en alguno de sus atributos. Creo que dejé esta como `True` en la entrega para poder probar bien las consultas.
- Hay un pequeño horrible bug con la función get_unique_movie_users en que no logra obtener todas las peliculas para cada actor/género. Esto hace que no se encuentren todos los successful_actors. Supongo que esto se debe a que se agota el iterador `movies`, pero aunque haya usado list(movies) esto no pareció arreglarse... Sorry :c

## Ubicación de consultas especificadas en el enunciado
- Funciones que retornan bases de datos: library/databases.py
- Funciones que no retornan bases de datos: libary/general.py
- Excepciones: library/exceptions.py
- Preprocesamiento: library/preproc.py

#### Ojala no me haya quedado demasiado roto todo :P