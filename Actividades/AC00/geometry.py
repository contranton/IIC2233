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
        super(self).init(position)
        self.radius = radius

    def get_area(self):
        return self.radius**2*pi

    def get_perimeter (self):
        return self.radius*pi*2
        
