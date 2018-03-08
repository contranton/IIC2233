from math import pi

class Shape:
    def __init__(self, position=(0, 0)):
        self.position = position

    def get_area(self):
        raise NotImplementedError()

    def get_perimeter(self):
        raise NotImplementedError()

    # Added another comment
    
class Circle (Shape):
    def __init__(self, position, radius):
        super().__init__(position)
        self.radius = radius

    def get_area(self):
        return self.radius**2*pi

    def get_perimeter(self):
        return self.radius*pi*2

    def __str__(self):
        return "Circle of radius %d at position (%d, %d)" %\
            (self.radius, *self.position)

class Rectangle (Shape):
    def __init__(self, position, width, height):
        super ().__init__(position)
        self.width = width
        self.height = height

    def get_area(self):
        return self.width*self.height

    def get_perimeter(self):
        return 2*self.width + 2*self.height

    def is_square(self):
        return self.width == self.height

    def __str__(self):
<<<<<<< HEAD
<<<<<<< HEAD
        return "Square with width %d and height %d located at (%i, %i)\n" %\
            (self.width, self.height, *self.position)

if __name__ == '__main__':
    c1 = Circle(position=(0, 0), radius=5)
    c2 = Circle(position=(4, 6), radius=10)

    r1 = Rectangle(position=(2, -4), width=5, height=5)
    r2 = Rectangle(position=(-3, 5), width=10, height=7)

    print(c1, c2, r1, r2)

    # Added a comment here
=======
        return "Square with width %d and height %d" %\
            (self.width, self.height)
>>>>>>> parent of 354d6de... Added __main__ block
=======
        return "Square with width %d and height %d" %\
            (self.width, self.height)
>>>>>>> parent of 354d6de... Added __main__ block
        
