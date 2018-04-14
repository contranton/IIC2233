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
        try:
            if index < 0:
                index = index % len(self)
            return getattr(self, self.__attr_name(index))
        except AttributeError:
            raise IndexError("xList index out of range")

    def __setitem__(self, key, val):
        setattr(self, self.__attr_name(key), val)

    def __delitem__(self, index):
        # Can't use range, can we? xd
        if index < 0:
            index = index % len(self)
        i = index
        # Shift indices left
        while i < len(self) - 1:
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
