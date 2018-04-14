class xList(object):
    def __init__(self, *args):
        "docstring"
        for i, value in enumerate(args):  # TODO: IS THIS LEGAL?
            setattr(self, "_" + str(i), value)

    def __getitem__(self, index):
        try:
            return getattr(self, "_" + str(index))
        except AttributeError:
            raise IndexError("xList index out of range")


if __name__ == '__main__':
    a = xList(1, 2, 3)
    print(a[0])
    
