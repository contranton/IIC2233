from sim import Simulation
from misc_lib import Logger
from events import schedule_initial_events

DEBUG = 1
Logger().PRINT = False

if __name__ == '__main__':
    # import pdb; pdb.set_trace()
    try:
        schedule_initial_events()
        Simulation().run()
    finally:
        Logger().write()
