import numpy as np

import game.parameters as params


class Entity:
    def __init__(self):
        """
        A generic entity that moves in the map.
        """

        # Negative position indicates being outside of the map
        self.position = np.array([-1, -1])

    def init_position(self, vec2):
        """
        Must receive a positional argument to place the player in the map.
        """
        self.position = np.array(vec2)

    def move(self, delta):
        self.position += delta


class Character(Entity):
    def __init__(self):
        """
        Main character class that handles player logic
        """
        self.lives = params.LIVES
        self.speed = params.SPEED
        self.immune_time = params.IMMUNE_TIME
