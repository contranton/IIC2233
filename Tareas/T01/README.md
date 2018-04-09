<div id="table-of-contents">
<h2>Table of Contents</h2>
<div id="text-table-of-contents">
<ul>
<li><a href="#sec-1">1. Tarea 1 &#x2013; Javier Contreras</a>
<ul>
<li><a href="#sec-1-1">1.1. Comentarios Generales</a></li>
<li><a href="#sec-1-2">1.2. Como usar el programa</a>
<ul>
<li><a href="#sec-1-2-1">1.2.1. Crear Galaxia</a></li>
<li><a href="#sec-1-2-2">1.2.2. Modificar Galaxia</a></li>
<li><a href="#sec-1-2-3">1.2.3. Consultar Galaxia</a></li>
<li><a href="#sec-1-2-4">1.2.4. Jugar con Galaxia</a></li>
</ul>
</li>
<li><a href="#sec-1-3">1.3. Supuestos Realizados</a></li>
<li><a href="#sec-1-4">1.4. Ubicación de requisitos principales</a></li>
</ul>
</li>
</ul>
</div>
</div>

# Tarea 1 &#x2013; Javier Contreras<a id="sec-1" name="sec-1"></a>

## Comentarios Generales<a id="sec-1-1" name="sec-1-1"></a>

-   Se recomienda iniciar el programa a través del archivo `run.bat` incluido (sorry por no tener version para bash :P), que se asegura de instalar los requisitos necesarios (paquetes `termcolor` y `colorama`). De otra manera, será necesario ejecutar `pip install -r requirements.txt` antes de correr `main.py`
-   El bloque `try: except` en el archivo `main` no existe para hacer pasar errores como si nada &#x2013; está solo para proveer feedback de por qué se habrá causado algun *crash* inesperado.

## Como usar el programa<a id="sec-1-2" name="sec-1-2"></a>

Al iniciar el programa te encontrarás en el menú principal donde tendrás cuatro acciones disponibles:
1.  Crear Galaxia
2.  Modificar Galaxia
3.  Consultar Galaxia
4.  Jugar en Galaxia
5.  Salir

En cualquiera de los menús con opciones demarcadas por un número, la manera de elegir una opción es simplemente ingresar el número y pulsar `ENTER`. Cuando sea posible, la última opción es "Volver" y permite regresar al menú anterior cancelando la acción actual.

A continuación se detalla cada posible opción:

### Crear Galaxia<a id="sec-1-2-1" name="sec-1-2-1"></a>

En esta serie de menús puedes crear una nueva galaxia, eligiendo primero su nombre y luego entrando a un *loop* donde puedes crear planetas, ingresando sus nombres y escogiendo sus razas, hasta saciarte. Una vez que decidas no seguir agregando más planetas, deberás elegir uno de ellos para comenzar conquistado, y habiendo terminado esto volverás al menú principal.

### Modificar Galaxia<a id="sec-1-2-2" name="sec-1-2-2"></a>

En este menú eligirás una galaxia para modificarla según tus deseos, sin preocuparte de deber gastar recursos para implementar mejoras. Al fin y al cabo, somos dioses!

Una vez seleccionada una galaxia, tienes las siguientes opciones, implementadas según el enunciado del problema:

1.  Agregar Planeta: Al igual que en el menú principal "Crear Galaxia", debes ingresar un nombre no antes usado para un planeta y elegir su raza.
2.  Eliminar planeta conquistado: Se despliegará una lista de los planetas conquistados en la galaxia, y al escoger uno para borrarse se te preguntará si efectivamente deseas continuar con la operación.
3.  Aumentar tasa de minerales: Se muestra cada planeta *sin conquistar* y su tasa actual al costado. Al elegir uno, se da la opción de ingresar un valor a sumarse definido por un valor mínimo y un máximo. En caso de que no sea posible agregar algo, estos dos simplemente se harán cero.
4.  Aumentar tasa de deuterio: Igual que el item anterior
5.  Agregar soldados: Se muestra cada planeta sin conquistar y su número de soldados actual. Al escoger uno, al igual que para el cambio de tasas, se da la opción de ingresar un valor cualquiera entre el minimo y maximo mostrados.
6.  Agregar magos: Igual que el item anterior pero para magos. Si la raza del planeta no es capaz de tener magos, se impedirá que se añadan.
    -   Hay un pequeño error en los valores actuales que se muestran en la selección de planeta. Estos son los soldados en vez de los magos, lo que se arregla cambiando el string "soldados" a "magos" en `menus.py:363`

### Consultar Galaxia<a id="sec-1-2-3" name="sec-1-2-3"></a>

Simplemente elige una opción para desplegar la información deseada. El único submenú con más interacción es el de "Inforamción de Planetas", donde aparecen los planetas ordenados por evolución y puedes elegir uno para obtener más información de él.

### Jugar con Galaxia<a id="sec-1-2-4" name="sec-1-2-4"></a>

Al escoger una galaxia con la que jugar, tendrás la opción de visitar un planeta o escribir cambios (hasta ahora inexistentes), lo que te devolverá al menú principal automáticamene. En el menú de selección de planetas, cada planeta tendrá indicado si está conquistado o no.

Al elegir un planeta, en el sector superior de la pantalla aparece información relevante como el nombre, población de soldados y magos, raza, y edificios existentes. Además, aparecen los recursos disponibles en la galaxia.

Para los planetas conquistados, tienes la opción de:
-   Construir edificios: Se indica si el edificio está construido o si puedes o no comprarlo.
-   Generar unidades: Dependiendo de si la raza del planeta admite magos, debes elegir primero si agregar soldados o magos, y luego elegir la cantidad a agregar. El máximo se calcula en base a los recursos disponibles y a la población máxima del planeta.
-   Recolectar recursos: Se muestran los recursos que podrías obtener al recolectar y la opción de hacerlo o no.
-   Implementar mejoras: Al igual que el menú de construcción de edificios, se muestra el nivel actual y el costo.

Para los planetas no conquistados, las opciones son:
-   Comprar el planeta: Si los recursos alcanzan, se te consultará si estas seguro de hacer la compra. En el caso contrario, se te informará de que no es posible realizar la transacción.
-   Invadir el planeta: Primero debes elegir un planeta conquistado para enviar su ejército. En caso de que ninguno tenga población, puedes regresar y cancelar la invasión sin problemas. En otro caso, se te consultará si estás seguro de actuar tan bélicamente y al afirmar comenzará la invasión. Cada turno muestra la vida actual de cada entidad, las habilidades usadas, el ataque generado por el agresor del turno y la vida final del defendiente de cada turno. Al terminar la batalla, se muestra quien ganó, se despliega el mensaje de victoria si esto aplica, y se regresa automáticamente al menú de visita de planetas.

Los eventos pueden ocurrir al visitar cualquier planeta, esté visitado o no. Para los asteroides, solo se muestra que el evento ocurrió en tal planeta sin obstaculizar la acción actual. En el caso de la invasión del archimago, se activa el menú de batalla correspondiente.

Es posible que un planeta sea conquistado instantáneamente debido a que tiene población 0. Esto puede suceder al momento en que el archimago invade un planeta conquistado sin mejoras, o cuando el jugador invade un planeta inicializado sin combatientes.

## Supuestos Realizados<a id="sec-1-3" name="sec-1-3"></a>

-   Cuando un archimago conquista el último planeta disponible en alguna galaxia, esta aún puede ser visitada pero no será posible invadir ningún planeta por no haber alguno conquistado de donde enviar un ejército. Sin embargo, debería poderse cambiar el estado de conquista a través del menú "Modificar Galaxia".
-   Al crear un planeta, si ha de comenzar conquistado parte con población 0, y si no, el 75% de población máxima se distribuye equitativamente entre soldados y magos, si aplica.

## Ubicación de requisitos principales<a id="sec-1-4" name="sec-1-4"></a>

Los siguientes links deberían funcionar vistos desde GitHub, mandándote a la línea en particular donde se define tal cosa.
-   [Atributos raza Maestro](./razas.py#L58)
-   [Atributos raza Aprendiz](./razas.py#L100)
-   [Atributos raza Asesino](./razas.py#L129)
-   [Clase Planeta](./universe.py#L97). Sus atributos son definidos en base a los nombres descritos en [\_planet<sub>defaults</sub>](./universe.py#L32) o aquellos existentes en los archivos `.csv`.
-   [Clase Galaxia](./universe.py#L237)
-   [Edificios](./universe.py#L56)
-   [Menu Crear Galaxia](./menus.py#L112)
-   [Menu Modify Galaxia](./menus.py#L210)
-   [Menu Consultar Galaxia](./menus.py#L381)
-   [Menu Jugar con Galaxia](./menus.py#L513)
-   [Evento Invasion Archimago](./menus.py#L630)
-   [Evento colision Asteroide](./menus.py#L651)
-   [Validacion de input](./menus_base.py) mediante métodos `_validate_input` para cada tipo de menu
-   [Lectura de csv](./file_io.py#L19)
-   [Escritura de csv](./file_io.py#L43)
-   [Sistema de batallas](./battle.py#L261)
-   [Constantes archimago](./battle.py#L17)
-   [Constantes planetas](./universe.py#L15)
