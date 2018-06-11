import numpy as np
from random import choice

from PyQt5.QtCore import QObject, pyqtSignal, QTimer

import parameters as params


class Entity(QObject):

    can_clip = False

    collidable = False
    collided = pyqtSignal(int)

    directions = np.array([[1, 0], [0, 1], [-1, 0], [0, -1]])

    id = 1

    def __init__(self, get_collidables_function):
        """
        A generic entity that moves in the map.
        """
        super().__init__()
        self.id = Entity.id
        Entity.id += 1

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
        pos = np.array(vec2).astype(int) + self.size/2# - [0, 0.01]
        self.position = pos

    def solid_corners(self, pos=None):
        pos = self.position if pos is None else pos
        return pos + self.size*self.bounds

    def move(self, dx, dy):

        # Negative position means player hasn't been set on map
        if all(self.position < 0):
            return None

        # Calculate new position based on map scale and player velocity
        scale = 1/params.TILE_SIZE
        dpos = np.array([dx, dy]) * scale
        new = self.position + dpos * self.velocity

        # Corners used for rectangular collision checking
        corners = self.solid_corners(new)

        if self.can_clip:
            self.position = new
            return None

        # Check for collisions
        # For each corner of our bounding rect
        solids, entities = self.get_collidable()
        for c in corners:
            # Gets solid at corner location
            solid = solids[tuple(c.astype(int))]
            if solid:
                self.collided.emit(solid.id)
                solid.collided.emit(self.id)
                return solid
        # Using this to not skip any collision checks when multiple
        # entities collide
        crashed = False
        # Collide with non-tile-size entities
        for entity in entities:
            if entity == self:
                continue
            # Adapted from
            # https://stackoverflow.com/questions/27152904/calculate-overlapped-area-between-two-rectangles
            # Because I don't know how to think xd
            others = entity.solid_corners()
            a, b = corners, others
            dx = min(a[3][0], b[3][0]) - max(a[0][0], b[0][0])
            dy = min(a[3][1], b[3][1]) - max(a[0][1], b[0][1])
            if dx >= 0 and dy >= 0:
                self.collided.emit(entity.id)
                entity.collided.emit(self.id)
                crashed = True
        if not crashed:
            # No collision
            self.position = new
            return None


class Bomb(QTimer, Entity):

    collidable=True
    explode_signal = pyqtSignal()
    collided = pyqtSignal(int)

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

        # Parameters for pushing it around
        self.moving = False
        self.direction = [0, 0]

    def timerEvent(self, *args):
        self.explode_signal.emit()
        self.stop()

    def update(self):
        self.move(*self.direction)

    def __repr__(self):
        return f"Bomb{self.num}"


class Character(Entity):
    __num = 1


    place_bomb_signal = pyqtSignal(Bomb)
    lives_changed = pyqtSignal(int)
    invincible_signal = pyqtSignal(bool)
    score_changed = pyqtSignal(int)

    bomb_num_increase = pyqtSignal()

    collidable = True

    def __init__(self, num, name, *args):
        """
        Main character class that handles player logic
        """
        super().__init__(*args)

        self.num = num
        self.name = name

        self.score = 0

        self.lives = params.LIVES
        self.speed = params.SPEED
        self.immune_time = params.IMMUNE_TIME

        self.invincible_timer = QTimer()
        self.invincible_timer.setSingleShot(True)
        self.invincible_timer.timeout.connect(self.end_invincibility)

        self.powerup_defuns = {"bomb":       self.powerup_bombs,
                               "life":       self.powerup_life,
                               "speed":      self.powerup_speed,
                               "superspeed": self.powerup_superspeed,
                               "juggernaut": self.powerup_juggernaut}

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

    def lose_health(self, other):
        if isinstance(other, Enemy) and not self.invincible_timer.isActive():
            self.lives = max(0, self.lives - 1)
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
        self.velocity = params.ENEMY_SPEED
        self.init_position(location)
        print(self.position)

        self.direction = None
        self.startTimer(1000*params.ENEMY_DIRECTION_TIME)
        self.timerEvent(None)

    def timerEvent(self, event):
        self.direction = choice([(1, 0), (-1, 0), (0, 1), (0, -1)])

    def auto_move(self):
        """
        Walks in a straight direction for some time before randomly
        choosing the next one
        """
        self.move(*self.direction)


class HostileEnemy(Enemy):
    def auto_move(self):
        pass


class Powerup(Entity):
    collidable = True
    taken = pyqtSignal()
    types = ["bomb", "life", "speed", "superspeed", "juggernaut"]

    def __init__(self, pos, *args):
        super().__init__(*args)
        self.init_position(pos)
        self.powerup_type = choice(self.types)
