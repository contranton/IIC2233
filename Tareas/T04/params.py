"""
Defines various numerical parameters used throughout the
simulation.
"""

from misc_lib import time_nt

###########################
# Simulation parameters   #
###########################

SIM_ITERATIONS = 100


#####################
# Park parameters   #
#####################

PARK_OPEN_TIME = time_nt(0, 10, 0)
PARK_CLOSE_TIME = time_nt(0, 19, 0)
PARK_OPERATORS_AT_GATE = 3

# Number of operators per number of rides
PARK_CLEANERS_PER_RIDE = 2
PARK_TECHS_PER_RIDE = 3

# Coefficient by which to multiply total ride capacity
PARK_TOTAL_CAPACITY_FACTOR = 1.2

#####################
# Worker parameters #
#####################

CLEANER_TRAVEL_TIME = 15

TECH_FIX_TIME = 20
TECH_TRAVEL_TIME = 15

# Probability of choosing an hour for lunch break. Starts from the
# 10:00-10:59 period and ends with the 18:00-18:59 one
WORKER_LUNCH_TIME_TABLE = [0.05, 0.05, 0.3, 0.2, 0.1, 0.1, 0.05, 0.05,
                           0.1]


#####################
# Client parameters #
#####################

# Height distributions
CLIENT_HEIGHT_ADULT_MU = 170
CLIENT_HEIGHT_ADULT_SIGMA = 8
CLIENT_HEIGHT_CHILD_MU = 120
CLIENT_HEIGHT_CHILD_SIGMA = 15

# Initial hungers
CLIENT_HUNGER_INITIAL_LOWER = 0.01
CLIENT_HUNGER_INITIAL_UPPER = 0.25

# Energy thresholds at which clients decide to leave
CLIENT_ENERGY_IMMEDATE_LEAVE_THRESHOLD = 0
CLIENT_ENERGY_MIGHT_LEAVE_THRESHOLD = 0.1
CLIENT_ENERGY_P_MIGHT_LEAVE = 0.5

# Clients' patience calculation
# Mu is a linear function of the energy of the client:
# mu = OFFSET + SLOPE * Energy_c
CLIENT_PATIENCE_MU_OFFSET = 10
CLIENT_PATIENCE_MU_SLOPE = 30
CLIENT_PATIENCE_SIGMA = 5

# Vomiting values
CLIENT_VOMIT_THRESHOLD = 90
CLIENT_VOMIT_CHANCE = 0.6
CLIENT_VOMIT_SETTLE = 50
CLIENT_NAUSEA_MAX = 150

# Factor multiplied to the group's average hunger
CLIENT_CHOOSE_RESTAURANT_MULT = 0.3

# Probability to go to a ride
CLIENT_P_RIDE = 0.7

# Time taken between each client action
CLIENT_DECISION_TIME = 10

# Break time
CLIENT_BREAK_TIME = 60
CLIENT_BREAK_ENERGY = 0.2

#########################
# Restaurant parameters #
#########################

# Preparation times
RESTAURANT_ADULT_PREP = 1/6
RESTAURANT_CHILD_PREP = 1/4

# Hunger and energy changes 
RESTAURANT_HUNGER_DELTA = -0.06
RESTAURANT_ENERGY_DELTA = 0.2

# Nausea added if just rode
RESTAURANT_AFTER_RIDE_NAUSEA = 30

#####################
# Ride parameters   #
#####################

# Nausea added after riding
RIDE_CHILD_NAUSEA_DELTA = 10
RIDE_ADULT_NAUSEA_DELTA = 5

# Energy delta after riding
RIDE_CHILD_ENERGY_DELTA = -0.05
RIDE_ADULT_ENERGY_DELTA = -0.15

# Hunger delta after riding
RIDE_CHILD_HUNGER_DELTA = 0.1
RIDE_ADULT_HUNGER_DELTA = 0.05

# Dirt added by vomiting
RIDE_VOMIT_DIRT = 40

# Dirt added by each user
RIDE_DIRT_DELTA = 1

# Maximum cleaning time by cleaners
RIDE_MAX_CLEANING_TIME = 10

#####################
# Misc parameters   #
#####################

SCHOOL_DAY_MIN_CHILDREN = 10
RUZILAND_FAILURE_RATE_FACTOR = 2
