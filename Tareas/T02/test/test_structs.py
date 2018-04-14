import unittest
from structs import xList


class TestXList(unittest.TestCase):

    def setUp(self):
        self.xList = xList(1, 2, 3)

    def test_indexing(self):
        with self.assertRaises(IndexError):
            self.xList[4]

        assert(self.xList[0] == 1)
        assert(self.xList[len(self.xList)] == 3)
        assert(self.xList[-1] == 3)
        assert(self.xList[-len(self.xList)] == 1)


if __name__ == '__main__':
    unittest.main()
