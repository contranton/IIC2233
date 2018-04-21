class _xIterator(object):
    def __init__(self, xlist, by_val=True):
        self.first = True
        self.current = xlist.first

        self.by_val = by_val

    def __iter__(self):
        return self

    def __next__(self):
        if self.current is None or\
           (self.current.next is None and not self.first):
            raise StopIteration
        else:
            if self.first:
                self.first = False
                return self.current.val if self.by_val else self.current
            self.current = self.current.next
            return self.current.val if self.by_val else self.current


class _listItem(object):
    def __init__(self, val, index):
        self.index = index
        self.val = val
        self.next = None

    def __iter__(self):
        return self

    def __repr__(self):
        s = "{}: {} -> {}"
        s = s.format(self.index, self.val,
                     type(self.next).__name__)
        return s


class xList(object):
    def __init__(self, *args):
        "docstring"
        i = 0
        current_item = None
        self.first = None
        for arg in args:
            if i == 0:
                current_item = _listItem(arg, i)
                self.first = current_item
                i += 1
                continue
            current_item.next = _listItem(arg, i)
            current_item = current_item.next
            i += 1
        self._len = i

    @staticmethod
    def __attr_name(index):
        return "_" + str(index)

    def __iter__(self):
        return _xIterator(self)

    def __eq__(self, other):
        for i, v in xEnum(self):
            try:
                if other[i] != v:
                    return False
            except IndexError:
                return False
        return True

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

        index = index % len(self)

        for x in _xIterator(self, by_val=False):
            if x.index == index:
                return x.val

    def __setitem__(self, index, val):
        if index >= len(self) or (index < 0 and abs(index) > len(self)):
            raise IndexError("xList assignment index out of range")

        index = index % len(self)

        for x in _xIterator(self, by_val=False):
            if x.index == index:
                x.val = val
                break

    def __delitem__(self, index):
        # Can't use range, can we? xd
        if index < 0:
            index = index % len(self)
        # Shift indices left
        for k in _xIterator(self, by_val=False):
            if k.index == index:
                aux = True
                while aux:
                    if k.next is None:
                        k = None
                        aux = False
                        break
                    k.val = k.next.val
                    k = k.next
                break

        self._len -= 1

    def append(self, item):
        if self.first is None:
            self.first = _listItem(item, 0)
            self._len = 1
            return
        for k in _xIterator(self, by_val=False):
            if k.next is None:
                k.next = _listItem(item, k.index + 1)
                break
        self._len += 1

    def pop(self, index=-1):
        item = self[index]

        del self[index]
        return item

    def remove(self, index):
        del self[index]

    def copy(self):
        return xList(*self)


def xEnum(L: xList):
    new_L = xList()
    i = 0
    for item in L:
        new_L.append(xList(i, item))
        i += 1
    return new_L
