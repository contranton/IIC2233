from structs.xList import xList, xEnum
from structs.xDict import xDict


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
            print(".",end="",flush=True)
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
        raise Exception("No node this graph contains %s" % str(content))

    def get_closest(self, orig, dest, transform=lambda x: x):
        # weight = transform(weight) such that in
        # best-match query we do transform=lambda x: 1-x
        # or something like that
        current = self.get_node_from_content(orig)
        dest = self.get_node_from_content(dest)

        # Dijkstra's algorithm
        visited = xList()
        unvisited = xList()

        # Set nearest neighbors to distance 0
        current.total_distance = 0

        while len(visited) > 0:
            for link in current.siblins:
                if link.dest in visited:
                    continue
                unvisited.append(link.dest)

            for link in current.siblings:
                link.dest.tentative_distance = current.total_distance +\
                                               transform(link.weight)
                link.dest.total_distance = min(link.dest.total_distance,
                                               link.dest.tentative_distance)
            visited.append(current)
            current = unvisited.pop(0)

            



if __name__ == '__main__':
    adj_matrix = xDict()
    items = xList("a", "b", "c")

    graph = xGraph(items)
    aNode = graph.nodes[0]
    bNode = graph.nodes[1]
    cNode = graph.nodes[2]

    aNode.add_sibling(bNode, 0.85)
    bNode.add_sibling(cNode, 0.5)
    aNode.add_sibling(cNode, 0.9)
