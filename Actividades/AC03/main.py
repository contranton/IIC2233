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
