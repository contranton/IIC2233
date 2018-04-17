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
    def __init__(self, content, siblings: xList=xList()):
        self.siblings = siblings  # type: xList[_xLink]
        self.content = content

    def __call__(self):
        return self.content

    def __repr__(self):
        return "Node(%s)" % str(self.content)

    def add_sibling(self, node, weight):
        link = _xLink(self, node, weight)
        if link not in self.siblings:
            self.siblings.append(link)
        else:
            return
            raise Exception("Connection between {} and {} "
                            "is already established".format(self, node))

    def __eq__(self, other):
        return self.content == other.content


class xGraph(object):

    def __init__(self):
        self.nodes = xList()

    def initialize_graph(self, adj_matrix):
        items = adj_matrix["items"]
        for i, row in xEnum(adj_matrix["mtx"]):
            for j, value in xEnum(row):
                if value != 0:
                    node = self.create_or_get_node(items[i])
                    dest = self.create_or_get_node(items[j])
                    node.add_sibling(dest, value)

    def create_or_get_node(self, content):
        new_node = xNode(content)
        for i, node in xEnum(self.nodes):
            # I.e., if content of nodes is equal,
            # don't overwrite the connections!
            if new_node == node:
                return node
        self.nodes.append(new_node)
        return new_node

    def get_all_shortest_paths(self):
        pass
        

if __name__ == '__main__':
    adj_matrix = xDict()
    adj_matrix["items"] = xList("A", "B", "C")
    adj_matrix["mtx"] = xList(xList(0, 1, 0.95),
                              xList(1, 0, 0),
                              xList(0.95, 0, 0))
    graph = xGraph(adj_matrix)
    ANode = graph.nodes[0]
    BNode = graph.nodes[1]
    CNode = graph.nodes[2]
        
