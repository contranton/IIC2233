import unittest
from structs.xList import xList
from structs.xDict import xDict
from structs.xGraph import xGraph


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

    def test_repr(self):
        print(self.xList)

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
        print(self.xDictNum)

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


class testXGraph(unittest.TestCase):

    def setUp(self):
        adj_matrix = xDict()
        adj_matrix["items"] = xList("A", "B", "C")
        adj_matrix["mtx"] = xList(xList(0, 1, 0.95),
                                  xList(1, 0, 0),
                                  xList(0.95, 0, 0))
        self.xGraph = xGraph(adj_matrix)
        self.ANode = self.xGraph.nodes[0]
        self.BNode = self.xGraph.nodes[1]
        self.CNode = self.xGraph.nodes[2]

    def test_siblings(self):
        assert(self.ANode.siblings[0].dest == self.BNode)
        assert(self.ANode.siblings[0].weight == 1)


if __name__ == '__main__':
    unittest.main()
