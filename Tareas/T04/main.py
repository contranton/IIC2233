from sim import Simulation

from events.client_events import schedule_arrivals

if __name__ == '__main__':
    import pdb
    schedule_arrivals()
    Simulation().run()
