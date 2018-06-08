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
        print(f"New position set to {self.position}")

    def move(self, dx, dy):
        # Negative position means player hasn't been set on map
        if all(self.position < 0):
            return

        # Calculate new position based on map scale and player velocity
        scale = 1/params.TILE_SIZE
        dx, dy = dx*scale, dy*scale
        new = self.position + np.array([dx, dy]) * self.velocity

        # Check for collisions
        if self.can_clip:
            self.position = new
            return
        else:
            # TODO: Colission checking
            #import pdb; pdb.set_trace()

            try:
                block = self.get_solids()[tuple(new.astype(int))]
                print(f"COllided with {block}")
            except KeyError:
                # No collision
                self.position = new
                return


class Character(Entity):
    def __init__(self, *args):
        """
        Main character class that handles player logic
        """
        super().__init__(*args)
        self.lives = params.LIVES
        self.speed = params.SPEED
        self.immune_time = params.IMMUNE_TIME
