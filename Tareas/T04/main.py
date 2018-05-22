import time

class Simulation:
    def __init__(self, model):
        self.time = 0
        self.model = model
        self.events_list = []

    def schedule(self, event, time_delta):
        event.update_time(self.time + time_delta)
        self.events_list.append(event)

    def run(self):
        self.time = time.time()
        self.model.generate_initial_events()
        while self.events_list:
            event = self.events_list.pop(0)
            new_events = event.run()
            for event, delta in new_events:
                self.schedule(event, delta)
        

if __name__ == '__main__':
    sim = Simulation(model=ModelNebiland)
    sim.run()
