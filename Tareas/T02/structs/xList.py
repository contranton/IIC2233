class xList(object):
    def __init__(self, *args):
        "docstring"
        i = 0
        for arg in args:
            setattr(self, self.__attr_name(i), arg)
            i += 1
        self._len = i

    @staticmethod
    def __attr_name(index):
        return "_" + str(index)

    def __iter__(self):
        self._n = 0
        return self

    def __next__(self):
        if self._n == len(self):
            raise StopIteration
        else:
            val = self[self._n]
            self._n += 1
            return val

    def __repr__(self):
        bckt_L = "--|"
        bckt_R = "|--"
        s = bckt_L
        L = xList()
        for i in self:
            L.append(str(i))
        s += ",".join(L) + bckt_R
        return s

    def __len__(self):
        return self._len

    def __getitem__(self, index):
        if index >= len(self) or (index < 0 and abs(index) > len(self)):
            raise IndexError("xList index out of range")
        return getattr(self, self.__attr_name(index % len(self)))

    def __setitem__(self, key, val):
        if key >= len(self) or (key < 0 and abs(key) > len(self)):
            raise IndexError("xList assignment index out of range")
        setattr(self, self.__attr_name(key % len(self)), val)

    def __delitem__(self, index):
        # Can't use range, can we? xd
        if index < 0:
            index = index % len(self)
        i = index + 1
        # Shift indices left
        while i < len(self):
            self[i - 1] = self[i]
            i += 1
        delattr(self, self.__attr_name(len(self) - 1))
        self._len -= 1

    def append(self, item):
        setattr(self, self.__attr_name(len(self)), item)
        self._len += 1

    def pop(self, index=-1):
        item = self[index]

        del self[index]
        return item

    def remove(self, index):
        del self[index]


def xEnum(L: xList):
    new_L = xList()
    i = 0
    for item in L:
        new_L.append(xList(i, item))
        i += 1
    return new_L
