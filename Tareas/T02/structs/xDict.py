from structs.xList import xList


class xDict(object):
    """
    Dammit, we can't use fast look-up without direct memory access T.T
    """
    def __init__(self, keys=None, values=None):

        self.__keys = keys if keys else xList()
        self.__values = values if values else xList()
        
        if len(self.__keys) != len(self.__values):
            raise ValueError("xDict constructor xLists have differing lenghts")

        self._len = 0
        i = 0
        while i < len(self.__keys):
            self[self.__keys[i]] = self.__values[i]
            self._len += 1
            i += 1

    def __iter__(self):
        raise Exception("xDict is not iterable")

    def keys(self):
        return self.__keys

    def values(self):
        return self.__values

    def items(self):
        return zip(self.__keys, self.__values)
    
    def __repr__(self):
        bckt_L = "--{"
        bckt_R = "}--"
        s = bckt_L
        L = xList()
        i = 0
        while i < len(self):
            L.append(str(self.__keys[i]) + ":" + str(self.__values[i]))
            i += 1
        s += ",".join(L) + bckt_R
        return s

    def __len__(self):
        return self._len

    def __getitem__(self, key):
        for key_, val in self.items():
            if key_ == key:
                return val
        raise KeyError("Key {} not in xDict".format(key))

    def __setitem__(self, key, val):
        if key not in self.__keys:
            self._len += 1
            self.__keys.append(key)
            self.__values.append(val)
        for key_, val_ in self.items():
            if key_ == key:
                val = val

    def __delitem__(self, key):
        raise NotImplementedError()


if __name__ == '__main__':
    a = xDict(xList(1,2,3), xList(5,6,7))
