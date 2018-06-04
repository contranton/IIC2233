import numpy as np

import parameters as params


class Entity:

    can_clip = False

    def __init__(self, get_solids_function):
        """
        A generic entity that moves in the map.
        """

        # Negative position indicates being outside of the map
        self.position = np.array([-1, -1])
        self.velocity = params.SPEED

        # Function that returns a map's solid blocks
        self.get_solids = get_solids_function

    def init_position(self, vec2):
        """
        Must receive a positional argument to place the player in the map.
        """
        self.position = np.array(vec2)
        print(self.position)

    def move(self, dx, dy):
        # Negative position means player hasn't been set on map
        if all(self.position < 0):
            return

        # Calculate new position based on map scale and player velocity
        scale = 1/params.TILE_SIZE
        dx, dy = dx*scale, dy*scale
        new = self.position + np.array([dx, dy]) * self.velocity

        print(new)
        # Check for collisions
        if self.can_clip:
            self.position = new
            return
        else:
            # TODO: Colission checking
            # self.position = new
            blocks = list(self.get_solids().items())
            # Returns tuple or other datathingy with position and tile
            # object. This allows the QPlayer to emit the
            # corresponding colission signal
            block = blocks[0][1]

            return block


class Character(Entity):
    def __init__(self, *args):
        """
        Main character class that handles player logic
        """
        super().__init__(*args)
        self.lives = params.LIVES
        self.speed = params.SPEED
        self.immune_time = params.IMMUNE_TIME
