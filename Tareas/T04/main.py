class Simulation:
    def __init__(self, model):
        self.model = model
        self.events_list = []

    def run(self):
        self.model.generate_initial_events()
        while self.events_list:
            event = self.events_list.pop(0)
            event.run()
        

if __name__ == '__main__':
    sim = Simulation(model=ModelNebiland)
    sim.run()
