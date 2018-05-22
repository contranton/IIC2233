from events.events_clients import EventClientArriveAtPark


class Model:
    def get_initial_events(self):
        return [(EventClientArriveAtPark, 1)]


class ModelNebiland(Model):
    pass


if __name__ == '__main__':
    from sim import sim
    sim.run()
    input()
