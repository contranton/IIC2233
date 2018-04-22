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
            print(".", end="", flush=True)
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

    def get_shortest_distance_multiple_dests(self, orig, destinations,
                                             transform=lambda x: x):
        """
        The graph MUST be connected, else not all destinations will 
        be reached
        """
        # weight = transform(weight) such that in
        # best-match query we do transform=lambda x: 1-x
        # or something like that
        
        if not isinstance(orig, xNode):
            current = self.get_node_from_content(orig)
        else:
            current = orig

        node_destinations = xList()
        for dest in destinations:
            if not isinstance(dest, xNode):
                node_destinations.append(self.get_node_from_content(dest))

        # Reset total and tentative distances
        for node in self.nodes:
            node.reset_distances()

        # Dijkstra's algorithm
        # Sourced from the one and only true source of completely
        # trustworthy information on the internet: Wikipedia
        # https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm
        visited = xList()
        unvisited = xList(current)

        # Set nearest neighbors to distance 0
        current.total_distance = 0
        current.tentative_distance = 0

        distances = xDict()

        ops = 0
        found = 1

        # Define this right away so we don't traverse it unnecesarily
        len_destinations = len(node_destinations)
        while unvisited:
            current = unvisited.pop()
#            import pdb; pdb.set_trace()
            # Get next nodes to traverse and add them to unvisited set
            for link in current.siblings:
                if link.dest in visited or link.dest in unvisited:
                    continue
                unvisited.append(link.dest)

            # Update distance for neighbors
            for link in current.siblings:
                ops += 1
                link.dest.tentative_distance = current.total_distance +\
                                               transform(link.weight)
                link.dest.total_distance = min(link.dest.total_distance,
                                               link.dest.tentative_distance)

            unvisited = unvisited.sort(key=lambda x: x.total_distance,
                                       reverse=True)
                
            # This node has now been visited
            visited.append(current)

            if current in node_destinations:
                found += 1
                distances[current.content] = current.total_distance

            if found == len_destinations:
                break

        print(ops)
        return distances.items()


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

    print(G.get_shortest_distance(ANode, DNode))
