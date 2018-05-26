from sim import Simulation
from events import schedule_initial_events

DEBUG = 1

if __name__ == '__main__':
    import pdb
    schedule_initial_events()
    Simulation().run()
