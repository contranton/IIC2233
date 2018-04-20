from structs.xList import xList


class xDict(object):
    """
    We store items using the id as an item reference.
    """
    def __init__(self, keys=xList(), values=xList()):
        if len(keys) != len(values):
            raise ValueError("xDict constructor xLists have differing lenghts")

        self.__keys = keys
        self.__values = values

        self._len = 0
        i = 0
        while i < len(keys):
            self[keys[i]] = values[i]
            self._len += 1
            i += 1

    @staticmethod
    def _attr_name(key):
        # If key isn't a nice number
        if not isinstance(key, int):
            if isinstance(key, str) and not key.isnumeric:
                # Yeah yeah, we use abs so we lose twice the namespace, but
                # we're still preeeetty unlikely to get collisions
                key = abs(hash(key))
        return "_" + str(key)

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
        while i < len(self) - 1:
            L.append(str(self.__keys[i]) + ":" + str(self.__values[i]))
            i += 1
        s += ",".join(L) + bckt_R
        return s

    def __len__(self):
        return self._len

    def __getitem__(self, key):
        try:
            return getattr(self, self._attr_name(key))[1]
        except AttributeError:
            raise KeyError("Key {} not in xDict".format(key))

    def __setitem__(self, key, val):
        if key not in self.__keys:
            self._len += 1
            self.__keys.append(key)
            self.__values.append(val)
        setattr(self, self._attr_name(key), xList(key, val))

    def __delitem__(self, key):
        raise NotImplementedError()


if __name__ == '__main__':
    a = xDict(xList(1,2,3), xList(5,6,7))
