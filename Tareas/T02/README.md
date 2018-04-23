# Consideraciones Generales
Es _absolutamente necesario_ que el programa se corra desde `main.py`, ya que este da la opción de elegir si realizar consultas al grafo de jugadores o simular campeonatos a través de la GUI, y maneja los posibles memes con los directorios e importación de paquetes (por esto hay un `__init__.py` no vacío en /GUI). Para este propósito, la sección de `Demo.py` que explicitaba "No cambiar hacia abajo" fue cambiada *solo* en cuanto se metió en una función `main()` en vez de el bloque `if __name__ == '__main__'`, para ser llamado desde `main.py`.

# Manual

Al correr `main.py` tendrás dos opciones: Realizar consultas sobre el grafo de jugadores, o simular un campeonato. Si eliges la primera, se te consultará cual base de datos usar (pequeña o grande) y luego se te pedirá que ingreses la ID de un jugador para ver todas sus estadísticas a la vez. Para listar las IDs posibles pulsa `h`, y para salir del programa, pulsa `q`. 

Al elegir simular campeonatos, se da la opción de usar modo 'simple' o modo 'real'. Estos son:
- Modo simple: Se calcula la afinidad solo entre jugadores del equipo del usuario. Para los otros, se utiliza una fórmula esotérica en base a la calidad del equipo. Esto permite testear rápidamente la generación de resultados y adquisición de consultas en el menú de campeonato.
- Modo real: Se calcula la afinidad para todos los equipos elegidos en un campeonato.
  - Solo cuando la base de datos escogida es la de 200 elementos este modo es viable; de otra manera, la asignacion inicial de las afinidades (las de 1, 0.95 y 0.9) de por sí ya será lenta por tener que iterar 18000^2 veces.
Al calcular las afinidades, la consola mostrará un indicador del equipo siendo analizado y valores correspondientes a las iteraciones sobre el grafo realizadas por cada jugador.

Hay un pequeño _bug_ en que si simulas campeonatos con tu equipo no completamente relleno y luego le intentas añadir jugadores, no podrás añadirlos todos ya que por alguna razón no logran eliminarse todos los jugadores provisorios que se le agregaron O.o

# Decisiones tomadas:
- Los equipos son obtenidos a partir de los jugadores ingresados a la GUI y su atributo `club`. Como estos son 200 de los totales, habrán equipos con menos jugadores asignados de los 11 totales. Para estos equipos, a la hora de simular el campeonato, se les añadiran jugadores de los otros equipos que no hayan sido seleccionados para jugar. Se asegura que estos siempre existirán pues 11*16 = 172 < 200. Al terminar el partido, estos son 'desasignados' y pueden volver a ser elegidos por otros equipos.
- Si el equipo jugador no tiene todos sus jugadores asignados desde el menu "Mi Equipo", se rellenara con jugadores aleatorios en el campeonato, al igual que en el item anterior.
- A la GUI se le entregan los equipos con el *numero de jugadores*, _no_ la afinidad como fue especificado. De esta manera, no es necesario esperar a que se calculen las afinidades para todos los equipos (largísimo :/) y aún así se da una indicación de mas o ménos cuánto se demoraría calcular la afinidad de tal equipo al seleccionarlo (ya que mas jugadores en un mismo club/equipo tienen mayor probabilidad de ser conocidos o de poseer caminos más cortos entre sí).

# Implementacion de Estructuras de Datos
Como estructuras 'puras' se implementaron: xList ~ list, xDict ~ dict, y xGraph.
Algunas estructuras afines incluyen xTournament (~arbol), xPlayer (contenedor simple), xGame.

Inicialmente se implemento xList usando `setattr` con nombre de atributo `_n` con 'n' el índice de la lista, pero como esto maneja el `__dict__` de la clase, resultó ser ilegal. La implementación final es a través de una _lista ligada_, en cuanto la clase xList posee un atributo `first` que apunta hacia el siguiente. El método __iter__ crea una clase Iteradora que toma el primer argumento y va retornando cada elemento de la lista ligada en __next__.

xDict consiste simplemente en dos xLists internos de `keys` y `values`, tal que al realizar una consulta sobre uno se itera sobre ambos (usando xDict.items(), que retorna un zip de los keys y values desenrollado en un xList) hasta encontrar el key deseado. Esto no esta ni llorando cerca de ser O(1) T.T
