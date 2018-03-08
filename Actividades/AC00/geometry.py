from math import pi

class Shape:
    def __init__(self, position=(0, 0)):
        self.position = position

    def get_area(self):
        raise NotImplementedError()

    def get_perimeter(self):
        raise NotImplementedError()

    
class Circle (Shape):
    def __init__(self, position, radius):
        super().__init__(position)
        self.radius = radius

    def get_area(self):
        return self.radius**2*pi

    def get_perimeter (self):
        return self.radius*pi*2


class Square (Shape):
    def __init__ (self, position, width, height):
        super ().__init__(position)
        self.width = width
        self.height = height

    def get_area (self):
        return self.width*self.height

    def get_perimeter (self):
        return 2*self.width + 2*self.height

    def is_square (self):
        return self.width == self.height
        
