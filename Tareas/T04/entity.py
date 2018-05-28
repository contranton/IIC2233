from random import normalvariate, expovariate, uniform, random, choices
from collections import deque

from faker import Faker

from fileio import get_associations
from sim import Simulation

# The M-q keybinding is the best hngggg
from params import (CLIENT_PATIENCE_MU_OFFSET,
                    CLIENT_PATIENCE_MU_SLOPE, CLIENT_PATIENCE_SIGMA,
                    CLIENT_VOMIT_THRESHOLD, CLIENT_VOMIT_CHANCE,
                    CLIENT_VOMIT_SETTLE, CLIENT_BREAK_ENERGY,
                    CLIENT_NAUSEA_MAX, CLIENT_HEIGHT_ADULT_MU,
                    CLIENT_HEIGHT_ADULT_SIGMA, CLIENT_HEIGHT_CHILD_MU,
                    CLIENT_HEIGHT_CHILD_SIGMA,
                    CLIENT_HUNGER_INITIAL_LOWER,
                    CLIENT_HUNGER_INITIAL_UPPER,
                    CLIENT_CRY_ADULT_ENERGY_DELTA,
                    CLIENT_CRY_CHILD_ENERGY_DELTA,
                    RUZILAND_FAILURE_RATE_FACTOR,
                    RIDE_MAX_CLEANING_TIME, RESTAURANT_ADULT_PREP,
                    RESTAURANT_CHILD_PREP, WORKER_LUNCH_TIME_TABLE)

fkr = Faker()


class Entity:
    """
    Generic Entity Class
    """
    # world = property(lambda _: IWorld().world)

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, self.name)


class Person(Entity):

    def __init__(self):
        """
        Generic Person Class
        """
        self.name = fkr.name()
        self._energy = 1
        self._nausea = 0
        self._budget = 0

        self._hunger = uniform(CLIENT_HUNGER_INITIAL_LOWER,
                               CLIENT_HUNGER_INITIAL_UPPER)

    @property
    def nausea(self):
        return self._nausea

    @nausea.setter
    def nausea(self, value):
        self._nausea = min(max(value, 0), CLIENT_NAUSEA_MAX)

    @property
    def hunger(self):
        return self._hunger

    @hunger.setter
    def hunger(self, value):
        self._hunger = min(max(value, 0), 1)

    @property
    def energy(self):
        return self._energy

    @energy.setter
    def energy(self, value):
        self._energy = min(max(value, 0), 1)

    @property
    def budget(self):
        return self._budget

    @budget.setter
    def budget(self, value):
        self._budget = value


class Client(Person):
    def __init__(self, budget, n_children):
        """
        Person that goes to the park with a budget and children in charge
        """
        super(Client, self).__init__()

        self.budget = budget
        self._height = normalvariate(CLIENT_HEIGHT_ADULT_MU,
                                     CLIENT_HEIGHT_ADULT_SIGMA)
        self.age = uniform(18, 60)

        self._children = []
        [self.add_child(Child()) for i in range(n_children)]

        self.rides_ridden = set()

        self.cant_ride_list = []
        self.client_id = None
        self.has_left = False
        self.got_on = False
        self.just_rode = False
        self.willing_to_queue = True

    def add_child(self, child):
        """
        Assign a child to this client
        """
        child.adult = self
        self._children.append(child)

    def vomit_and_cry(self):
        """
        Simulate possibility of vomiting and crying for the children
        """
        num = 0
        for p in [self] + [c for c in self._children]:
            if p.nausea > CLIENT_VOMIT_THRESHOLD and\
               random() < CLIENT_VOMIT_CHANCE:
                num += 1
                p.nausea = CLIENT_VOMIT_SETTLE
            elif isinstance(p, Child):
                if p.cry():
                    self.energy += CLIENT_CRY_ADULT_ENERGY_DELTA
                    p.energy += CLIENT_CRY_CHILD_ENERGY_DELTA
        return num

    def enough_budget(self, costs):
        """
        Verify if the client's budget can satisfy the given costs
        """
        total = costs[0] + costs[1]*len(self.children)
        return total < self.budget

    def pay(self, costs):
        """
        Pay the specified costs, removing the money from the available
        budget
        """
        total = costs[0] + costs[1]*len(self.children)
        self.budget -= total

    @property
    def children(self):
        return [c.name for c in self._children]

    @property
    def group_size(self):
        return 1 + len(self._children)

    @property
    def patience(self):
        return int(normalvariate(
            CLIENT_PATIENCE_MU_OFFSET +
            CLIENT_PATIENCE_MU_SLOPE*self._energy,
            CLIENT_PATIENCE_SIGMA))

    @property
    def num_children(self):
        return len(self._children)

    @property
    def _all_energies(self):
        return [self._energy] + [c._energy for c in self._children]

    @property
    def _all_hungers(self):
        return [self._hunger] + [c._hunger for c in self._children]

    @property
    def _all_heights(self):
        return [self._height] + [c._height for c in self._children]

    def any_height_below(self, height):
        return any(map(lambda x: x < height, self._all_heights))

    @property
    def minimum_energy(self):
        return min(self._all_energies)

    def any_energy_less_than(self, value):
        return any(map(lambda x: x < value, self._all_energies))

    @property
    def average_hunger(self):
        return sum(self._all_hungers) / (self.num_children + 1)

    def rest(self):
        """
        Simulate the act of taking a break
        """
        self._energy = min(self._energy + CLIENT_BREAK_ENERGY, 1)
        for c in self._children:
            c._energy = min(c._energy + CLIENT_BREAK_ENERGY, 1)

    def raise_child_nauseas(self, delta):
        for c in self._children:
            c._nausea = min(max(c._nausea + delta, 0), CLIENT_NAUSEA_MAX)

    def raise_child_hungers(self, delta):
        for c in self._children:
            c._hunger = min(max(c._hunger + delta, 0), 1)

    def raise_child_energies(self, delta):
        for c in self._children:
            c._energy = min(max(c._energy + delta, 0), 1)


class Child(Person):
    def __init__(self):
        """
        Person with a responsible adult client
        """
        super(Child, self).__init__()
        self._height = normalvariate(CLIENT_HEIGHT_CHILD_MU,
                                     CLIENT_HEIGHT_CHILD_SIGMA)
        self.adult = None
        self.age = uniform(1, 17)

    def cry(self):
        """
        Boolean that specifies whether child has cried or no
        """
        return random() < (1 - self.age/18)**2


class Worker(Entity):
    def __init__(self):
        """
        Generic entity whose work is managed by the park
        """
        self.name = fkr.name()
        self.busy = False

        self.lunch_hour = choices(range(10, 19),
                                  weights=WORKER_LUNCH_TIME_TABLE)[0]

    def __repr__(self):
        s = ":BUSY" if self.busy else ":FREE"
        return super().__repr__() + s

    def close_down_responsabilities(self):
        """
        Finalize work actions before going for break
        """
        pass

    def open_up_responsabilities(self):
        """
        Restart work actions after returning from break
        """
        pass


class Attraction(Entity):
    def __init__(self, id, name, type_, adult_cost, child_cost, capacity,
                 duration, min_height, dirt_limit, max_time):
        """
        Ride in the park with parameters specified in the .csv file

        Manages the queue of people waiting to ride
        """
        self.id = int(id)
        self.name = name
        self.type = type_
        self.adult_cost = int(adult_cost)
        self.child_cost = int(child_cost)
        self.capacity = int(capacity)
        self.duration = int(duration)
        self.min_height = int(min_height)
        self.dirt_limit = int(dirt_limit)
        self.max_time = int(max_time)
        self._dirt = 0

        self.queue = deque()
        self.failed = False
        self.started = False
        self.just_ended = True

        self._serviced = False
        self._time_begin_oos = 0

        self.time_with_at_least_one_person = None

    def __repr__(self):
        return "Ride({}:{})".format(self.id, self.name)

    def add_to_queue(self, client):
        """
        Inserts client into the queue

        If queue was empty before, triggers the automated entry to the
        ride after the ride's max_time
        """
        if len(self.queue) == 0:
            self.start_countdown()
        self.queue.appendleft(client)

    def start_countdown(self):
        """
        Schedules entry to the ride in case its capacity hasn't been fully
        occupied
        """
        from events.park_events import schedule_forced_start
        schedule_forced_start(self)

    def remove_from_queue(self, client):
        """
        Removes a client from the queue
        """
        self.queue.remove(client)

    def start(self):
        """
        Begins the ride, setting the appropiate states and executing the
        appropiate callback to schedule next events
        """
        from events.client_events import callback_enter_ride
        from events.park_events import schedule_ride_start

        self.started = True

        cap = self.capacity
        riders = [self.queue.pop()
                  for i in range(min(cap, len(self.queue)))]
        [callback_enter_ride(rider, self) for rider in riders]

        self.time_with_at_least_one_person = 0
        schedule_ride_start(self)

    def can_begin(self):
        """
        Boolean that asserts if ride can begin without being forced
        """
        if self._serviced:
            return False
        else:
            return len(self.queue) >= self.capacity

    def fail(self):
        """
        Sets the ride as having failed
        """
        self.failed = True

    @property
    def dirt(self):
        return self._dirt

    @dirt.setter
    def dirt(self, value):
        self._dirt = min(max(value, 0), self.dirt_limit)

    @property
    def costs(self):
        return (self.adult_cost, self.child_cost)

    @property
    def over_dirt_limit(self):
        return self.dirt > self.dirt_limit

    @property
    def failure_rate(self):
        from model import World
        rate = 1 / (self.capacity * self.duration)
        if World().ruziland:
            rate *= RUZILAND_FAILURE_RATE_FACTOR
        return rate

    @property
    def time_cleaning(self):
        max_cleaning_time = RIDE_MAX_CLEANING_TIME
        return min(self.dirt - self.dirt_limit, max_cleaning_time)

    @property
    def closed(self):
        from model import Nebiland, World
        if not Nebiland().open:
            return True
        if World().raining and self.type == "acuatica":
            return True
        return False

    def out_of_service(self):
        """
        Starts servicing of the ride, rendering it unusable until
        back_in_service is called
        """
        self._serviced = True
        self._time_begin_oos = Simulation().time.raw()

    def back_in_service(self):
        """
        Returns the ride into service
        """
        self._serviced = False
        new_t = Simulation().time.raw()
        self._times_oos = new_t - self._time_begin_oos
        self._time_begin_oos = new_t


class Restaurant(Entity):
    def __init__(self, id, name, capacity, adult_cost,
                 child_cost, max_duration):
        """
        Restaurant object
        """
        self.id = int(id)
        self.name = name
        self.capacity = int(capacity)
        self.adult_cost = int(adult_cost)
        self.child_cost = int(child_cost)
        self.max_duration = int(max_duration)

        self.inside = 0

        self.rides = {ride for restaurant, ride in get_associations()
                      if restaurant == self.id}

    @property
    def costs(self):
        return (self.adult_cost, self.child_cost)

    def enough_capacity(self, size):
        return self.inside + size < self.capacity

    @property
    def time_cooking_adult(self):
        return int(expovariate(RESTAURANT_ADULT_PREP))

    @property
    def time_cooking_child(self):
        return int(expovariate(RESTAURANT_CHILD_PREP))
