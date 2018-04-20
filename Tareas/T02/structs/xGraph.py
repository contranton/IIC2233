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
        if not siblings:
            self.siblings = xList()
        else:
            self.siblings = siblings  # type: xList[_xLink]

        self.content = content

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

    def __init__(self, items=xList()):
        # Initialized floating, i.e. with no connections
        self.nodes = xList()
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

    def get_shortest_path(self, transform=lambda x: x):
        # weight = transform(weight) such that in
        # worst-match query we do transform=lambda x: 1-x
        # or something like that
        pass
        

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
