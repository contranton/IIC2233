import numpy as np

from collections import defaultdict
from random import uniform, expovariate, sample, choice

from PyQt5.QtCore import QObject, pyqtSignal, QTimer


from game.tiles import make_tile, Ground
from game.entities import (Character, HostileEnemy, Enemy, Bomb,
                           Powerup, Entity)
from parameters import (ENEMY_DOCILE_A, ENEMY_DOCILE_B,
                        ENEMY_HOSTILE_LAMBDA, ENEMY_SPAWN_CLEARANCE,
                        MAX_ENEMIES)


class Map(QObject):


    bomb_laid_signal = pyqtSignal(Bomb)
    powerup_placed_signal = pyqtSignal(Powerup)
    new_enemy_signal = pyqtSignal(Enemy)

    finished = pyqtSignal()
    
    # Dictionary with ids of all tiles and important entities used for
    # some particularly pesky signals
    everything = {}

    def __init__(self, map_path, names):
        """
        Holder for all tiles with their coordinates

        Coordinates are 0-indexed, and origin is at the top-left of
        the map.txt file.
        """
        super().__init__()

        # Dictionary of the form:
        # position(i, j): Tile
        self.tiles = {}
        self.solids = defaultdict(lambda: None)

        # Loads map from file
        self.load_map(map_path)

        # True if a block has changed. Initially true on creation to
        # allow setting of solid blocks
        self.map_changed = True

        # Players contained in map
        self.p1 = Character(1, names[0], self.get_collidable)
        self.p2 = Character(2, names[1], self.get_collidable)
        for p in (self.p1, self.p2):
            p.place_bomb_signal.connect(self.place_bomb)
            p.bomb_num_increase.connect(self.increase_max_bombs)
            p.collided.connect(self.player_collide)
            p.died_signal.connect(self.finish)
            self.everything[p.id] = p

        self.entities = [self.p1, self.p2]
        self.__active_bombs = 0
        self.max_bombs = 1
        self.max_enemies = MAX_ENEMIES

        self._docile_enemy_timer = QTimer()
        self._docile_enemy_timer.setSingleShot(True)
        self._docile_enemy_timer.timeout.connect(self.create_docile_enemy)

        self._hostile_enemy_timer = QTimer()
        self._hostile_enemy_timer.setSingleShot(True)
        self._hostile_enemy_timer.timeout.connect(self.create_hostile_enemy)

        self.start_enemy_timers()

    def player_collide(self, id_):
        player = self.sender()
        other = self.everything[id_]
        player.lose_health(other)

    def increase_max_bombs(self):
        self.max_bombs += 1

    def valid_enemy_locations(self):
        p1_pos = self.p1.position
        p2_pos = self.p2.position

        empties = np.array([k for (k, v) in self.tiles.items()
                            if not v.solid]).astype(float)

        dists1 = np.linalg.norm(empties - p1_pos, axis=1)
        dists2 = np.linalg.norm(empties - p2_pos, axis=1)

        dists = np.min([dists1, dists2], axis=0)

        valid = empties[np.nonzero(dists > ENEMY_SPAWN_CLEARANCE)]
        valid = valid.astype(int)

        return list(map(tuple, valid))

    def start_enemy_timers(self):
        from game.entities import DIFFICULT
        p = 0.5 if DIFFICULT else 1
        if not self._docile_enemy_timer.isActive():
            self._docile_enemy_timer.start(uniform(ENEMY_DOCILE_A,
                                                   ENEMY_DOCILE_B)*1000*p)
        if not self._hostile_enemy_timer.isActive():
            self._hostile_enemy_timer.start(
                expovariate(1/ENEMY_HOSTILE_LAMBDA)*1000*p
            )

    @property
    def num_enemies(self):
        return len(list(filter(lambda x: isinstance(x, Enemy), self.entities)))

    def _create_enemy(self, EnemyType):
        if self.num_enemies >= self.max_enemies:
            return
        location = choice(self.valid_enemy_locations())

        enemy = EnemyType(location, self.get_collidable)
        enemy.dead.connect(self.enemy_dead)

        self.entities.append(enemy)
        self.everything[enemy.id] = enemy
        print("enemy created")

        self.new_enemy_signal.emit(enemy)
        self.start_enemy_timers()

    def create_docile_enemy(self):
        self._create_enemy(Enemy)

    def create_hostile_enemy(self):
        self._create_enemy(HostileEnemy)

    def enemy_dead(self):
        enemy = self.sender()
        try:
            self.entities.remove(enemy)
        except:
            input("We've had trouble deleting enemies. Debug pls")
            import pdb; pdb.set_trace()

        self.start_enemy_timers()

    def load_map(self, map_path):
        """
        Reads map file and creates appropiate tile objects
        """

        # Read file
        map_str = []
        with open(map_path, 'r') as file:
            for row in file.readlines():
                map_str.append(row.strip().split(" "))

        # Create Tiles with map position as key
        for i, row in enumerate(map_str):
            for j, tile_str in enumerate(row):
                pos = (i, j)
                tile = make_tile(tile_str, pos)
                tile.exploded_signal.connect(self.change_tile)
                self.tiles[pos] = tile
                self.everything[tile.id] = tile

    def change_tile(self):
        tile = self.sender()
        self.map_changed = True
        self.tiles[tile.position].change(Ground)

    def all_empty_tiles_in_sight(self, pos):
        pos = pos.astype(int)
        tiles = [self.tiles[tuple(pos)]]
        for direction in [(-1, 0), (1, 0), (0, 1), (0, -1)]:
            collided = False
            current = pos.copy()
            
            while not collided:
                current += direction
                tile = self.tiles[tuple(current)]
                if tile.solid:
                    collided = True
                    if not tile.breakable:
                        continue
                tiles.append(tile)
        return tiles

    def get_collidable(self):
        """
        Gets solid blocks as seen by entity, i.e., an entity won't see
        itself as an obstsacle
        """
        # Update solid blocks only if a bomb has destroyed a block
        if self.map_changed:
            self.solids.update({k: (v if v.solid else None)
                                for k, v in self.tiles.items()})
            self.map_changed = False

        # Get solid-like entities
        collidables = [e for e in self.entities if e.collidable]
        return (self.solids, collidables)

    def place_bomb(self, bomb):
        if self.__active_bombs >= self.max_bombs:
            return

        self.__active_bombs += 1
        bomb.explode_signal.connect(self.bomb_explode)
        bomb.collided.connect(self.bomb_push)
        self.bomb_laid_signal.emit(bomb)
        self.entities.append(bomb)
        self.everything[bomb.id] = bomb

    def bomb_push(self, id_):
        pusher = self.everything[id_]
        bomb = self.sender()
        
        if isinstance(pusher, Entity):
            bomb.moving = True

            delta = bomb.position - pusher.position

            # Keep only the maximum value
            delta[np.abs(delta) < np.max(np.abs(delta))] = 0

            # Only care about the direction. Remember our coordinates
            # are origin top-left!
            delta = np.sign(delta)

            bomb.direction = delta

        
    def bomb_explode(self):
        self.__active_bombs -= 1

        bomb = self.sender()
        self.entities.remove(bomb)

        pos = bomb.position.astype(int)
        self.map_changed = True
        for tile in self.all_empty_tiles_in_sight(pos):
            powerup = tile.explode()
            if powerup:
                self.create_powerup(powerup)

    def create_powerup(self, powerup):
        print("Powerup has been created")
        powerup.taken.connect(self.remove_powerup)
        powerup.collided.connect(self.assign_powerup)
        self.powerup_placed_signal.emit(powerup)
        self.entities.append(powerup)

    # Slot
    def assign_powerup(self, id_):
        sender = self.everything[id_]
        powerup = self.sender()

        if isinstance(sender, Character):
            sender.powerup_defuns[powerup.powerup_type]()
            powerup.taken.emit()

    def remove_powerup(self):
        sender = self.sender()
        try:
            self.entities.remove(sender)
        except:
            input("Something has gone terribly wrong")
            import pdb; pdb.set_trace()

    def finish(self):
        self.finished.emit()
