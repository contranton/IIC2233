# Number of ms per each timer event
TICK_RATE = 10

# Number of pixels moved per tick
SPEED = 2

# Number of lives
LIVES = 3

# Time an explosion persists on screen in s
EXPLOSION_TIME = 2

# Explosion range. -1 for infinite
EXPLOSION_RANGE = -1

# Immunity time after being damaged
IMMUNE_TIME = 2

# Maximum default number of enemies on screen at any time. This may
# vary in-game when difficulty increases
MAX_ENEMIES = 1

# Range of sight for enemies. -1 for infinite
ENEMY_SIGHT = 5

# Enemy speed
ENEMY_SPEED = 1.2

# Uniform distribution parameters for docile enemies in seconds
ENEMY_DOCILE_A = 5
ENEMY_DOCILE_B = 10

# Exponential distribution rate for hostile enemies in Hz
ENEMY_HOSTILE_LAMBDA = 4

# Radius in tiles of space around the player where enemies can't spawn
ENEMY_SPAWN_CLEARANCE = 5

# Tile dimensions in pixels. Tiles are always square
TILE_SIZE = 50

# Animation speed for movement with multiple frames.
ANIM_SPEED = 20  # Measured in Hz
