from sim import Simulation
from misc_lib import Logger
from events import schedule_initial_events

DEBUG = 0
Logger().PRINT = False

if __name__ == '__main__':
    import pdb
    try:
        Simulation().run(max_iterations=1,
                         event_creator=schedule_initial_events)
    except:
        import traceback as tb; tb.print_exc()
        if DEBUG:
            pdb.pm()
        else:
            input("Wiiii me caí :D")
    finally:
        Logger().write()

    # import pdb; pdb.set_trace()
