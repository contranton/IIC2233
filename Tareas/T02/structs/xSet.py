from structs.xList import xList


class xSet():
    def __init__(self, args=None):
        self.content = args if args else xList()
        self.__ensure_unique()

    def __iter__(self):
        return iter(self.content)

    def __eq__(self, other):
        return self.content == other

    def __repr__(self):
        s = "++|{}|++"
        s = s.format(",".join(map(lambda x: str(x), self.content)))
        return s

    def __ensure_unique(self):
        for item in self:
            for other in self:
                if item == other:
                    del other

    def add(self, *other):
        for item in other:
            if item not in self.content:
                self.content.append(item)

    def union(self, other):
        new = xSet(self.content)
        for item in other:
            if item not in new:
                new.content.append(item)
        return new

    def intersection(self, other):
        new = xSet()
        for item in other:
            if item in self.content:
                new.content.append(item)
        new.__ensure_unique()
        return new

    def __and__(self, other):
        return self.intersection(other)

    def __or__(self, other):
        return self.union(other)
