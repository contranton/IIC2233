import numpy as np
from random import choice

from PyQt5.QtCore import QObject, pyqtSignal, QTimer

import parameters as params


class Entity(QObject):

    can_clip = False

    collidable = False
    collided = pyqtSignal()

    directions = np.array([[1, 0], [0, 1], [-1, 0], [0, -1]])

    def __init__(self, get_collidables_function):
        """
        A generic entity that moves in the map.
        """
        super().__init__()

        # Negative position indicates being outside of the map.  It's
        # also super far away so that it doesn't get interpreted as
        # being near the map, as for example when an enemy can't spawn
        # too close to the character locations
        self.position = np.array([-100, -100])
        self.velocity = params.SPEED

        # Specifies which corners define the bounding box used in collisions
        self.size = np.array([0.5, 1])
        self.bounds = np.array([[-0.5, 0], [-0.5, 0.5], [0.5, 0], [0.5, 0.5]])

        # Function that returns a map's solid blocks
        self.get_collidable = get_collidables_function

    def init_position(self, vec2):
        """
        Must receive a positional argument to place the player in the map.
        """
        # TODO: Shift to non solid block
        pos = np.array(vec2).astype(int)# + self.size/2 - [0, 0.01]
        self.position = pos

    def move(self, dx, dy):

        # Negative position means player hasn't been set on map
        if all(self.position < 0):
            return None

        # Calculate new position based on map scale and player velocity
        scale = 1/params.TILE_SIZE
        dpos = np.array([dx, dy]) * scale
        new = self.position + dpos * self.velocity

        # Corners used for rectangular collision checking
        corners = (new + self.size*self.bounds).astype(int)

        if self.can_clip:
            self.position = new
            return None
        
        # Check for collisions
        # For each corner of our bounding rect
        for c in map(tuple, corners):
            solids, entities = self.get_collidable()
            solid = solids[c]
            entity = entities[c]
            if solid:
                solid.collided.emit()
                self.collided.emit()
                return solid
            elif entity and self != entity:
                entity.collided.emit()
                self.collided.emit()
                return entity
        # No collision
        self.position = new
        return None


class Bomb(QTimer, Entity):

    explode_signal = pyqtSignal()

    __num = 0

    def __init__(self, player_num, pos, *args):
        super().__init__(*args)
        self.num = Bomb.__num
        Bomb.__num += 1

        self.player_placed = player_num
        self.init_position(pos)
        print(self.position)
        self.setSingleShot(True)
        self.start(params.EXPLOSION_TIME * 1000)

    def timerEvent(self, *args):
        self.explode_signal.emit()
        self.stop()

    def pushed(self, pusher_pos):
        delta = self.position - pusher_pos
        return delta

    def __repr__(self):
        return f"Bomb{self.num}"


class Character(Entity):
    __num = 1


    place_bomb_signal = pyqtSignal(Bomb)
    lives_changed = pyqtSignal(int)
    invincible_signal = pyqtSignal(bool)

    bomb_num_increase = pyqtSignal()
    
    collidable = True

    def __init__(self, *args):
        """
        Main character class that handles player logic
        """
        super().__init__(*args)

        self.num = self.__num
        Character.__num += 1

        self.lives = params.LIVES
        self.speed = params.SPEED
        self.immune_time = params.IMMUNE_TIME

        self.invincible_timer = QTimer()
        self.invincible_timer.setSingleShot(True)
        self.invincible_timer.timeout.connect(self.end_invincibility)

    def __repr__(self):
        return f"Player(#{self.num}, {self.lives} lives)"

    def __str__(self):
        return f"Player#{self.num}"

    def begin_invincibility(self, time):
        self.invincible_timer.start(time*1000)
        self.invincible_signal.emit(True)

    def end_invincibility(self):
        self.invincible_signal.emit(False)
    
    def place_bomb(self):
        bomb = Bomb(self.num, self.position, self.get_collidable)
        self.place_bomb_signal.emit(bomb)

    def move(self, *args):
        collided = super().move(*args)
        if not collided:
            return
        elif (isinstance(collided, Enemy) and not
              self.invincible_timer.isActive()):
            self.lives -= 1
            self.lives_changed.emit(self.lives)
            self.begin_invincibility(params.IMMUNE_TIME)

    # Powerups
            
    def powerup_life(self):
        self.lives = min(self.lives + 1, params.LIVES)

    def powerup_bombs(self):
        self.bomb_num_increase.emit()

    def powerup_speed(self):
        self.velocity *= 1.25

    def powerup_superspeed(self):
        def end(self):
            self.velocity /= 3
        self.velocity *= 3
        timer = QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(end)
        timer.start(10)

    def powerup_juggernaut(self):
        self.begin_invincibility(5)


class Enemy(Entity, QTimer):

    collidable = True
    velocity = params.ENEMY_SPEED

    dead = pyqtSignal()

    def __init__(self, location, *args):
        "docstring"
        super().__init__(*args)
        self.lives = 1
        self.init_position(location)

        self.direction = None
        self.choose_direction()

        self.collided.connect(self.choose_direction)

    def find_direction(self):
        np.random.shuffle(self.directions)
        for direction in self.directions:
            new = tuple((self.position + direction).astype(int))

            if not self.get_collidable()[0][new]:
                return direction

        # If we couldn't find a direction it's cus we've been blocked,
        # so return the same direction to allow the game to continue
        # and check again in the next collision event
        return self.direction

    def choose_direction(self):
        self.direction = self.find_direction()

    def auto_move(self):
        """
        Walks in a straight line until collision. This is the default
        behavior
        """
        self.move(*self.direction)


class HostileEnemy(Enemy):
    def auto_move(self):
        pass


class Powerup(Entity):
    collidable = True
    types = ["bomb", "life", "speed", "superspeed", "juggernaut"]

    def __init__(self, *args):
        super().__init__(*args)
        self.powerup_type = choice(self.types)[0]
