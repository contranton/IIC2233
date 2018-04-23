import unittest
from structs.xList import xList
from structs.xDict import xDict
from structs.xGraph import xGraph
from structs.xSet import xSet


class TestXList(unittest.TestCase):

    def setUp(self):
        self.xList = xList(1, 2, 3)

    def test_indexing(self):
        with self.assertRaises(IndexError):
            self.xList[3]
            self.xList[-4]

        assert(self.xList[0] == 1)
        assert(self.xList[len(self.xList) - 1] == 3)
        assert(self.xList[-1] == 3)
        assert(self.xList[-len(self.xList)] == 1)

    def test_iterating(self):
        assert(xList(*self.xList) == xList(1, 2, 3))
        nested = [i*j for i in self.xList for j in self.xList]
        assert(nested == [1, 2, 3, 2, 4, 6, 3, 6, 9])

    def test_repr(self):
        str(self)

    def test_containment(self):
        assert(2 in xList(1, 2, 3))
        assert(3 not in xList(1, 2))
        a = xDict()
        assert(a in xList(a, 1, 2))

    def test_assignment(self):
        self.xList[0] = 4
        assert(self.xList[0] == 4)

    def test_append(self):
        self.xList.append(4)
        assert(self.xList[-1] == 4)
        assert(len(self.xList) == 4)

    def test_pop(self):
        self.xList.append(4)

        last = self.xList.pop()
        assert(last == 4)
        assert(len(self.xList) == 3)

        first = self.xList.pop(0)
        assert(first == 1)
        assert(self.xList[-1] == 3)

    def test_remove(self):
        self.xList.remove(0)
        assert(self.xList[0] == 2)
        assert(len(self.xList) == 2)


class TestXDict(unittest.TestCase):

    def setUp(self):
        self.xDictNum = xDict(xList(1, 2, 3, 4, 5),
                              xList("a", "b", "c", "d", "e"))

        self.xDictStr = xDict(xList("a", "b", "c", "d", "e"),
                              xList(1, 2, 3, 4, 5))

    def test_creation(self):
        xDict(xList(1, 2, 3), xList("a", "b", "c"))

        with self.assertRaises(ValueError):
            xDict(xList(1, 2, 3), xList("a", "b"))

        xDict(xList(), xList())

    def test_repr(self):
        str(self)

    def test_access(self):
        assert(self.xDictNum[1] == "a")
        assert(self.xDictNum[5] == "e")
        assert(self.xDictStr["a"] == 1)
        assert(self.xDictStr["e"] == 5)

    def test_addition(self):
        self.xDictNum[6] = "f"
        self.xDictStr["f"] = 6
        assert(self.xDictNum[6] == "f")
        assert(self.xDictStr["f"] == 6)

        assert(len(self.xDictNum) == 6)

    def test_delete(self):
        del self.xDictNum[5]
        assert(len(self.xDictNum) == 4)
        with self.assertRaises(KeyError):
            self.xDictNum[5]


class testXGraph(unittest.TestCase):

    def setUp(self):
        items = xList(*"abcd")
        self.xGraph = xGraph(items)
        self.ANode = self.xGraph.nodes[0]
        self.BNode = self.xGraph.nodes[1]
        self.CNode = self.xGraph.nodes[2]
        self.DNode = self.xGraph.nodes[3]

        self.ANode.add_sibling(self.BNode, 1)
        self.ANode.add_sibling(self.CNode, 5)
        self.BNode.add_sibling(self.CNode, 2)
        self.BNode.add_sibling(self.DNode, 4)
        self.CNode.add_sibling(self.DNode, 1)

    def test_siblings(self):
        assert(self.ANode.siblings[0].dest == self.BNode)
        assert(self.ANode.siblings[0].weight == 1)
        assert(self.BNode.siblings[0].dest == self.ANode)
        assert(self.BNode.siblings[1].dest == self.CNode)
        assert(self.BNode.siblings[1].weight == 2)

    # @unittest.skip("Dijkstra not Implemented")
    def test_shortest(self):
        assert(self.xGraph.get_shortest_distance(self.ANode, self.CNode) == 3)
        assert(self.xGraph.get_shortest_distance(self.ANode, self.DNode) == 4)
        assert(self.xGraph.get_shortest_distance(self.CNode, self.DNode) == 1)

        assert(self.xGraph.get_shortest_distance(self.ANode, self.ANode) == 0)


class testXSet(unittest.TestCase):
    def setUp(self):
        self.xSet = xSet(xList(1, 2, 3, 4))

    def test_add(self):
        self.xSet.add(*xList(3, 4, 5, 6))
        assert(xList(*self.xSet) == xList(1, 2, 3, 4, 5, 6))

        self.xSet.add(10)
        assert(xList(*self.xSet) == xList(1, 2, 3, 4, 5, 6, 10))

    def test_intersection(self):
        new = self.xSet & xSet(xList(3, 4, 5, 6))
        assert(xList(*new) == xList(3, 4))

    def test_union(self):
        new = self.xSet | xSet(xList(3, 4, 5, 6))
        assert(xList(*new) == xList(1, 2, 3, 4, 5, 6))
        
        
if __name__ == '__main__':
    unittest.main()
