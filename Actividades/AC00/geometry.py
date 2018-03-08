from math import pi

class Shape:
    def __init__(self, position=(0, 0)):
        self.position = position

    def get_area(self):
        raise NotImplementedError()

    def get_perimeter(self):
        raise NotImplementedError()

        
