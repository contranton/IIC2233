from structs.xList import xList, xEnum
from structs.xDict import xDict
from structs.xSet import xSet


class _xLink(object):
    def __init__(self, orig, dest, weight):
        self.orig = orig
        self.dest = dest
        self.weight = weight

    def __repr__(self):
        s = "{} <-({})-> {}".format(str(self.orig),
                                    str(self.weight),
                                    str(self.dest))
        return s

    def __eq__(self, other):
        return ((self.orig == other.orig and
                 self.dest == other.dest) or
                (self.orig == other.dest and
                 self.dest == other.orig))


class xNode(object):
    """
    Undirected, i.e. only siblings, no 'parents' or 'children'
    """
    def __init__(self, content, siblings=None):
        self.siblings = siblings if siblings else xList()  # xList[_xLink]
        self.content = content
        self.reset_distances()

    def __id__(self):
        return id(self.content)

    def reset_distances(self):
        # For dijkstra
        self.total_distance = 1000000
        self.tentative_distance = 1000

    def __call__(self):
        return self.content

    def __repr__(self):
        return "Node(%s)" % str(self.content)

    def add_sibling(self, node, weight):
        # import pdb; pdb.set_trace()
        link = _xLink(self, node, weight)
        if link not in self.siblings:
            self.siblings.append(link)
            node.siblings.append(_xLink(node, self, weight))
        else:
            return
            raise Exception("Connection between {} and {} "
                            "is already established".format(self, node))

    def __eq__(self, other):
        return self.content == other.content


class xGraph(object):

    def __init__(self, items=None):
        # Initialized floating, i.e. with no connections
        self.nodes = xList()
        items = items if items else xList()
        for item in items:
            self.nodes.append(self.create_or_get_node(item))

    def create_or_get_node(self, content, trust_all_different=True):
        new_node = xNode(content)
        # If we can be sure all incoming items will be different
        # so we don't have to do an O(n^2) loop to check for belonging
        if not trust_all_different:
            for i, node in xEnum(self.nodes):
                # I.e., if content of nodes is equal,
                # don't overwrite the connections!
                if new_node == node:
                    return node
        return new_node

    def get_node_from_content(self, content):
        for n in self.nodes:
            if n.content == content:
                return n
        raise Exception("No node in this graph contains %s" % str(content))

    def __iter__(self, initial_node):
        return iter(xIterGraphDijkstra(self, initial_node))

    def get_shortest_distance(self, orig, dest, transform=lambda x: x):
        for step in xIterGraphDijkstra(self, orig, transform):
            if step.current == dest:
                return step.current.total_distance
        return None

    def get_shortest_distance_multiple_dests(self, orig, destinations,
                                             transform=lambda x: x):

        """
        Returns an xList with the distance to each destination in the form:
        [(dest1, dist1), (dest2, dist2), ...]

        As xLists, obviously ;)
        """
        node_destinations = xList()
        for dest in destinations:
            if not isinstance(dest, xNode):
                node_destinations.append(self.get_node_from_content(dest))

        distances = xDict()

        ops = 0
        found_dests = 1

        # Define this right away so we don't traverse it unnecesarily
        len_destinations = len(node_destinations)

        for step in xIterGraphDijkstra(self, orig, transform):
            current = step.current

            # If goal node has been found, get its distance
            if current in node_destinations:
                found_dests += 1
                distances[current.content] = current.total_distance

            # We've found all we care about, quit!
            if found_dests == len_destinations:
                break

            ops = step.ops

        print(ops)
        return distances.items()

    def get_closest(self, orig, transform=lambda x: x):
        closest = None

        last = None
        for step in xIterGraphDijkstra(self, orig, transform):
            last = step
            continue

        closest = min(
            filter(lambda n: n != last.initial_node, last.visited),
            key=lambda s: s.total_distance)

        return closest

    def get_nearest(self, orig, threshold, transform=lambda x: x):
        vis = xList()
        for step in xIterGraphDijkstra(self, orig, transform):
            vis.append(step.current)
            for i, unvis in xEnum(step.unvisited):
                if unvis.total_distance > threshold:
                    step.unvisited.pop(i)
                    step.visited.append(unvis)
        # First element is always origin
        try:
            vis.pop(0)
        except IndexError:
            return xList()
        return vis


class xIterGraphDijkstra(object):
    """
    Implements Dijkstra's algorithm iteratively

    Sourced from the one and only true source of completely
    trustworthy information on the internet: Wikipedia
    https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm
    """
    def __init__(self, graph, initial_node, transform=lambda x: x):

        self.graph = graph

        # Reset total and tentative distances
        for node in self.graph.nodes:
            node.reset_distances()

        # Ensure initial is a node
        if not isinstance(initial_node, xNode):
            self.current = self.graph.get_node_from_content(initial_node)
        else:
            self.current = initial_node

        self.initial_node = self.current

        # Transforms weights uniformly
        self.transform = transform

        self.unvisited = xList(self.initial_node)
        self.visited = xList()
        self.current = self.initial_node

        # Set nearest neighbors to distance 0
        self.current.total_distance = 0
        self.current.tentative_distance = 0

        self.ops = 0

    def __iter__(self):
        return self

    def __next__(self):
        if not self.unvisited:
            raise StopIteration

        self.current = self.unvisited.pop()

        for link in self.current.siblings:
            self.ops += 1

            # Update distances between nodes
            link.dest.tentative_distance = (self.current.total_distance +
                                            self.transform(link.weight))
            link.dest.total_distance = min(link.dest.total_distance,
                                           link.dest.tentative_distance)

            # Add siblings to unvisited set if eligible
            if link.dest in self.visited or link.dest in self.unvisited:
                continue
            self.unvisited.append(link.dest)

        # Make it so the next node to visit is the closest one
        self.unvisited = self.unvisited.sort(key=lambda x: x.total_distance,
                                             reverse=True)

        self.visited.append(self.current)

        return self

if __name__ == '__main__':
    items = xList(*"abcd")
    G = xGraph(items)
    ANode = G.nodes[0]
    BNode = G.nodes[1]
    CNode = G.nodes[2]
    DNode = G.nodes[3]

    ANode.add_sibling(BNode, 1)
    ANode.add_sibling(CNode, 5)
    BNode.add_sibling(CNode, 2)
    BNode.add_sibling(DNode, 4)
    CNode.add_sibling(DNode, 1)

    print(G.get_shortest_distance(ANode, BNode, transform=lambda x: x))
    print(G.get_shortest_distance(ANode, CNode, transform=lambda x: x))
    print(G.get_shortest_distance(ANode, DNode, transform=lambda x: x))
