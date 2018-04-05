from collections import deque

class GraphNode:
    def __init__(self, nombre):
        self.value = nombre
        self.destinations = set()

    def link_forward(self, node):
        self.destinations.add(node)

    def remove_link(self, node):
        self.destinations.discard(node)

    def __repr__(self):
        s = self.value
        return s


class Graph:
    def __init__(self):
        # dict {node_name: value}
        self.nodes = {}

    def cargar_archivo(self, path_archivo):
        with open(path_archivo, 'r') as file:
            for line in file.readlines():
                origin, destination = line.strip().split(",")
                # Create nodes if they don't exist already
                for value in {origin, destination}:
                    if value not in self.nodes:
                        self.nodes[value] = GraphNode(value)

                self.agregar_conexion(origin, destination)

    def agregar_conexion(self, origen, destino):
        or_node, de_node = self.nodes[origen], self.nodes[destino]
        or_node.link_forward(de_node)

    def quitar_conexion(self, origen, destino):
        or_node, de_node = self.nodes[origen], self.nodes[destino]
        or_node.remove_link(de_node)

    def _add_children_to_queue(self, queue, node, visited_nodes):
        """Anadir nodos al queue a menos que ya hayan sido visitados

        El uso de esta operacion obliga a que la iteracion sobre el queue
        se haga por medio de un checkeo de longitud o similar y un pop()
        adentro ya que de otra manera se levanta un error por mutar el
        queue durante su iteracion.
        """
        [queue.append(child)
         for child in node.destinations
         if child not in visited_nodes]

    def encontrar_camino(self, origen, destino):
        origin_node = self.nodes[origen]

        visited = {origin_node}  # type: set
        queue = deque()

        self._add_children_to_queue(queue, origin_node, visited)

        while len(queue) != 0:

            node = queue.pop()
            visited.add(node)

            if node.value == destino:
                return True

            self._add_children_to_queue(queue, node, visited)


        return False


    def encontrar_camino_corto(self, origen, destino):
        return ''

    def export_csv(self, path_archivo):
        with open(path_archivo, 'w') as file:
            for node in self.nodes.values():
                name = node.value
                for d_name in map(lambda x: x.value, node.destinations):
                    file.write(",".join([name, d_name]) + "\n")
            

if __name__ == "__main__":
    print("*" * 20 + "EASY" + "*" * 20)
    grafo_facil = Graph()
    grafo_facil.cargar_archivo("easy.txt")
    print(grafo_facil.encontrar_camino("A", "C"))  # True
    print(grafo_facil.encontrar_camino("B", "A"))  # False
    print(grafo_facil.encontrar_camino_corto("A", "E"))  # [A, B, E]
    print(grafo_facil.encontrar_camino_corto("A", "C"))  # [A, C]
    grafo_facil.quitar_conexion("A", "C")
    print(grafo_facil.encontrar_camino("A", "C"))  # True
    print(grafo_facil.encontrar_camino_corto("A", "C"))  # [A, B, E, C]
    grafo_facil.quitar_conexion("B", "E")
    print(grafo_facil.encontrar_camino("A", "C"))  # True
    print(grafo_facil.encontrar_camino_corto("A", "C"))  # [A, B, D, E, C]
    grafo_facil.quitar_conexion("D", "E")
    print(grafo_facil.encontrar_camino("A", "C"))  # False
    grafo_facil.agregar_conexion("A", "C")
    print(grafo_facil.encontrar_camino("A", "C"))  # True
    grafo_facil.export_csv("easy_output.txt")  # A,B
                                               # A,C
                                               # B,D
                                               # E,C

    print("\n" + "*" * 20 + "MEDIUM" + "*" * 20)
    grafo_medium = Graph()
    grafo_medium.cargar_archivo("medium.txt")
    print(grafo_medium.encontrar_camino("A", "G"))  # True
    print(grafo_medium.encontrar_camino("A", "D"))  # True
    print(grafo_medium.encontrar_camino_corto("A", "G"))  # [A, F, G]
    grafo_medium.quitar_conexion("A", "F")
    grafo_medium.quitar_conexion("A", "I")
    grafo_medium.quitar_conexion("A", "M")
    grafo_medium.quitar_conexion("A", "D")
    grafo_medium.quitar_conexion("A", "E")
    print(grafo_medium.encontrar_camino("A", "G"))  # False

    print("\n" + "*" * 20 + "HARD" + "*" * 20)
    grafo_hard = Graph()
    grafo_hard.cargar_archivo("hard.txt")
    print(grafo_hard.encontrar_camino_corto("A", "Z"))  # [A, 0, 4, 5, L, Z]
    print(grafo_hard.encontrar_camino("A", "G"))  # True
    grafo_hard.agregar_conexion("4", "Z")
    print(grafo_hard.encontrar_camino_corto("A", "Z"))  # [A, 0, 4, Z]
    grafo_hard.quitar_conexion("4", "Z")
    print(grafo_hard.encontrar_camino_corto("A", "Z"))  # [A, 0, 4, 5, L, Z]
    print(grafo_hard.encontrar_camino("X", "Z"))  # False
    grafo_hard.agregar_conexion("X", "B")
    print(grafo_hard.encontrar_camino("X", "Z"))  # True
    print(grafo_hard.encontrar_camino_corto("X", "Z"))  # [X, B, T, L, Z]
