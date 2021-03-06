from random import random, choice, choices
from functools import partial

from events import Event
from entity import Client, Child
from sim import Simulation
from model import Nebiland, World
from fileio import get_arrivals
from misc_lib import datetime_to_time, Logger

# I f****ng love emacs
from params import (PARK_OPEN_TIME, PARK_CLOSE_TIME,
                    CLIENT_ENERGY_IMMEDATE_LEAVE_THRESHOLD,
                    CLIENT_ENERGY_MIGHT_LEAVE_THRESHOLD,
                    CLIENT_ENERGY_P_MIGHT_LEAVE,
                    CLIENT_CHOOSE_RESTAURANT_MULT, CLIENT_P_RIDE,
                    CLIENT_DECISION_TIME, CLIENT_BREAK_TIME,
                    RESTAURANT_ADULT_PREP, RESTAURANT_CHILD_PREP,
                    RESTAURANT_HUNGER_DELTA, RESTAURANT_ENERGY_DELTA,
                    RESTAURANT_AFTER_RIDE_NAUSEA,
                    RIDE_CHILD_NAUSEA_DELTA, RIDE_ADULT_NAUSEA_DELTA,
                    RIDE_VOMIT_DIRT, RIDE_DIRT_DELTA,
                    SCHOOL_DAY_MIN_CHILDREN, RIDE_CHILD_ENERGY_DELTA,
                    RIDE_ADULT_ENERGY_DELTA, RIDE_CHILD_HUNGER_DELTA,
                    RIDE_ADULT_HUNGER_DELTA, RUZILAND_LEAVE_CHANCE)


def schedule_arrivals():
    """
    Schedules all the client arrivals throughout the week.
    """
    for day, time, budget, children in get_arrivals():
        # Create new clients
        client = Client(budget, children)

        # Log clients to DAQ
        Logger().all_clients.append(client)

        # Client enters
        event_enter = Event("ClientArrives", client, client_enter_park)
        Simulation().schedule(event_enter, time=datetime_to_time(day, time))


def client_enter_park(client):
    """
    Event callback: manages whether a client can enter the park or
    not.

    Checks for time of entry, park capacity, and external events
    """
    # Ensures limit and capacity as well as school day restrictions

    def leave_event(reason, add=True):
        if add:
            Logger().people_left_due_to_events.append(client)
        return Event("ClientForbiddenEntry{}"
                     .format(reason), client,
                     client_cant_enter)

    # Client arrives too late
    if (Simulation().time.time()) > PARK_CLOSE_TIME.time():
        event = leave_event("TooLate", add=False)
        Simulation().schedule(event)
        return

    if not Nebiland().has_capacity(client.group_size):
        event = leave_event("ParkIsFull", add=False)
        Simulation().schedule(event)
        return

    # If adult doesn't have enough children during a school day
    if World().school_day and len(client.children) < SCHOOL_DAY_MIN_CHILDREN:
        event = leave_event("TooFewChildrenInSchoolDay")
        Simulation().schedule(event)
        return

    # If adult has too many kids on a rain day
    if World().raining and len(client.children) > 1:
        event = leave_event("TooManyChildrenInRainDay")
        Simulation().schedule(event)
        return

    # Client enters just fine
    c_id = Nebiland().client_enters(client.name, client.num_children)
    client.client_id = c_id

    client_decide_next_action(client)

    # Schedule forced leave at the closing time
    # event_leave = Event("ClientLeaveDueToClosing", client, client_leave)
    # Simulation().schedule(event_leave, time=Nebiland().closing_time_today,
    #                      obsolete_if=lambda client: client.has_left)


def ensure_park_open(client):
    """
    Checks that the park hasn't closed and schedules a departure if it has.

    Must be incorporated in event callbacks before they schedule new
    events to be useful.

    Returns a bool indicating whether the park has closed or
    not. Useful to return prematurely from callbacks
    """
    if (Simulation().time.time()) >= PARK_CLOSE_TIME.time():
        event_leave = Event("ClientLeavesDueToClosing", client, client_leave)
        Simulation().schedule(event_leave)
        client.energy_at_exit = client.energy
        return False
    return True


def client_decide_next_action(client):
    """
    Decides what a client will do next and schedules the event accordingly
    """

    # Apply ruziland criterion
    if World().ruziland and not client.decided_ruziland:
        if random() < RUZILAND_LEAVE_CHANCE:
            client.decided_ruziland = True
            Logger().people_left_due_to_events.append(client)
            event = Event("ClientLeavesDueToInvasion", client, client_leave)
            Simulation().schedule(event)
            return

    # If client has left an installation but park has closed, must leave
    if not ensure_park_open(client):
        return

    # If clients don't have enough energy, they leave
    min_energy = client.minimum_energy
    if min_energy <= CLIENT_ENERGY_IMMEDATE_LEAVE_THRESHOLD:
        event = Event("ClientLeavesDueToEnergy", client, client_leave)
        Simulation().schedule(event)
        Logger().num_left_by_lack_of_energy += 1
        client.left_due_to_energy = True
        return
    elif client.any_energy_less_than(CLIENT_ENERGY_MIGHT_LEAVE_THRESHOLD):
        if random() < CLIENT_ENERGY_P_MIGHT_LEAVE:
            event = Event("ClientLeavesDueToEnergy", client, client_leave)
            Simulation().schedule(event)
            Logger().num_left_by_lack_of_energy += 1
            client.left_due_to_energy = True
            return

    # If clients don't have enough budget, leave
    if client.budget < Nebiland().minimum_budget(client.num_children,
                                                 client.rides_ridden,
                                                 client.cant_ride_list):
        event = Event("ClientLeavesDueToBudget", client, client_leave)
        Simulation().schedule(event)
        client.energy_at_exit = client.energy
        return

    # Randomly choose the next place to go

    # Check preemptively if client has any available rides
    ride = choose_ride(client)

    # No chance of going to a restaurant if they haven't gone to the
    # necessary ride

    restaurant_p = client.average_hunger * CLIENT_CHOOSE_RESTAURANT_MULT
    restaurant_p *= Nebiland().any_valid_restaurants(client.rides_ridden)

    queue_p = client.willing_to_queue * (ride is not None) * CLIENT_P_RIDE

    p = random()
    if p < queue_p:
        # Goto ride
        foo = partial(client_goto_ride, ride=ride)
        event = Event("ClientGoesToRide", client, foo,
                      extra_info=lambda: str(ride))
        Simulation().schedule(event, delta=CLIENT_DECISION_TIME,
                              on_open_hours=True)
    elif queue_p < p < queue_p + restaurant_p:
        # Goto restaurant
        event = Event("ClientGoesToRestaurant", client, client_goto_restaurant)
        Simulation().schedule(event, delta=CLIENT_DECISION_TIME,
                              on_open_hours=True)
    else:
        # Rest
        #import pdb; pdb.set_trace()

        event = Event("ClientBeginsBreak", client, client_take_break)
        Simulation().schedule(event, delta=CLIENT_DECISION_TIME,
                              on_open_hours=True)


def client_leave(client):
    """
    Event callback: Client exits park due to lack of budget
    """
    Nebiland().client_exits(client.client_id)
    client.has_left = True


def client_cant_enter(client):
    """
    Event callback: Client not allowed into the park
    """
    pass


def client_goto_restaurant(client):
    """
    Event callback: Client goes to restaurant after having decided they
    can indeed go to one.

    This shouldn't be called without first checking there is a valid
    restaurant, even though said restaurant might be over capacity.

    Schedules food preparation events
    """
    # Client might not get to the installation in time before park closes
    if not ensure_park_open(client):
        return

    # Restaurant selection
    valid_restaurants = Nebiland().get_valid_restaurants(client.rides_ridden)
    restaurant = choice(valid_restaurants)

    def forbidden(reason):
        Logger().num_people_couldnt_eat += 1
        return Event(
            "ClientNotAllowedInRestaurant{}"
            .format(reason), client, client_decide_next_action,
            extra_info=lambda: str(restaurant))

    if not client.enough_budget(restaurant.costs):
        event = forbidden("TooExpensive")
        Simulation().schedule(event)
        return

    if not restaurant.enough_capacity(client.group_size):
        event = forbidden("IsFull")
        Simulation().schedule(event)
        return

    # Bookkeep entry into restaurant
    Simulation().schedule(Event("ClientEntersRestaurant", client,
                                lambda e: None,
                                extra_info=lambda: str(restaurant)))

    client.enter_restaurant(Simulation().time)

    # Food preparation
    time_entered = Simulation().time.raw()
    in_restaurant = partial(client_in_restaurant,
                            restaurant=restaurant,
                            time_entered=time_entered)
    event = Event("ClientPreparesFood", client, in_restaurant)
    Simulation().schedule(event,
                          delta=restaurant.time_cooking_adult,
                          on_open_hours=True)
    for child in client.children:
        event = Event("ChildPreparesFood", child, lambda e: None)
        Simulation().schedule(event,
                              delta=restaurant.time_cooking_child,
                              on_open_hours=True)


def client_in_restaurant(client, restaurant, time_entered):
    """
    Event callback: Schedules time of departure from restaurant
    """
    event = Event("ClientLeavesRestaurant", client, client_leave_restaurant)
    max_time = restaurant.max_duration + time_entered
    Simulation().schedule(event, time=max_time)


def client_leave_restaurant(client):
    """
    Event callback: Client leaves restaurant and its effects are
    applied.

    Immediately schedules the next action through client_decide_next_action
    """

    # Possible nausea increase
    if client.just_rode:
        client.nausea += RESTAURANT_AFTER_RIDE_NAUSEA
        client.raise_child_nauseas(RESTAURANT_AFTER_RIDE_NAUSEA)

    # Hunger and energy updates
    client.hunger += RESTAURANT_HUNGER_DELTA
    client.energy += RESTAURANT_ENERGY_DELTA
    client.raise_child_hungers(RESTAURANT_HUNGER_DELTA)
    client.raise_child_energies(RESTAURANT_ENERGY_DELTA)

    # State changes
    client.willing_to_queue = True
    client.just_rode = False
    client_decide_next_action(client)


def client_take_break(client):
    """
    Event callback: Client takes a break

    Schedules end of break
    """
    if not ensure_park_open(client):
        return
    event = Event("ClientFinishesBreak", client, client_finish_break)
    Simulation().schedule(event, delta=CLIENT_BREAK_TIME,
                          on_open_hours=True)


def client_finish_break(client):
    """
    Event callback: Client finishes break and applies effects

    Immediately schedules the next action through
    client_decide_next_action
    """
    client.rest()
    client.willing_to_queue = True
    client.just_rode = False
    if not ensure_park_open(client):
        return
    client_decide_next_action(client)


def choose_ride(client):
    """
    Attempts to return a valid ride that a client knows they can go
    to. Returns either such a ride with a probability inversely
    proportional to their queue length or None if no such ride is
    found.
    """
    rides = list(filter(lambda r: r not in client.cant_ride_list,
                        Nebiland().attractions_by_queue_length))

    # Checks if no ride is valid for this group in terms of minimum
    # height or budget
    if all(map(lambda r: r in client.cant_ride_list, rides)):
        return None

    # Returns a valid ride with higher priority for the ones with
    # shortest queues
    ride = choices(rides, weights=map(lambda r: 1/(len(r.queue)+1), rides))
    return ride[0] if ride else None


def client_goto_ride(client, ride):
    """
    Event callback: Client arrives at ride and finds out whether they
    fit the height requirement and have enough budget.

    Schedules departure from the ride in case of invalidity or entry
    into the queue
    """
    # Client might not get to the installation in time before park closes
    if not ensure_park_open(client):
        return

    ################
    # Cases in which client might be turned away from ride
    foo = partial(client_cant_ride, ride=ride)

    def leave_event(reason): return Event("ClientNotAllowedInRide{}"
                                          .format(reason), client, foo,
                                          extra_info=lambda: str(ride))

    if not client.any_height_below(ride.min_height):
        event = leave_event("TooShort")
        Simulation().schedule(event)
        return

    if not client.enough_budget(ride.costs):
        event = leave_event("InsufficientBudget")
        Simulation().schedule(event)
        return
    ################

    # Client enters ride queue successfuly
    enter_ride = partial(client_enter_ride_queue, ride=ride)
    event = Event("ClientEntersQueueForRide", client, enter_ride,
                  extra_info=lambda: str(ride))
    Simulation().schedule(event)


def client_cant_ride(client, ride):
    """
    Event callback: Client forbidden to ride a certain ride either due
    to height or budget. Ride is added to this client's 'no-ride' list
    """
    client.cant_ride_list.append(ride)
    client_decide_next_action(client)


def client_enter_ride_queue(client, ride):
    """
    Event callback: Client enteres ride queue.

    Schedules obsoletable loss of patience and adds client to ride's
    queue for internal management
    """
    # Schedule conditional event whereby client loses patience
    exit_queue = partial(client_exits_queue, ride=ride)
    event = Event("ClientLosesPatienceInQueue", client, exit_queue,
                  extra_info=lambda: str(ride))
    Simulation().schedule(event, delta=int(client.patience),
                          obsolete_if=lambda client: client.got_on,
                          on_open_hours=True)
    client.enter_queue(Simulation().time)
    ride.add_to_queue(client)


def callback_enter_ride(client, ride):
    """
    External callback: Client finishes queue and enters the
    ride. Called only from the ride's queue manager to ensure everyone
    finishes at the same time. That is, this CAN'T be scheduled a
    priori.

    Schedules entry to the ride (for bookkeeping purposes) and the
    departure from the ride
    """
    # Log the event of having finished the queue
    Simulation().schedule(Event("ClientEntersRide", client, lambda e: None,
                                extra_info=lambda: str(ride)))

    client.got_on = True
    client.pay(ride.costs)
    client.left_queue(Simulation().time)

    # Schedule getting off the ride
    leave_ride = partial(client_leaves_ride, ride=ride)
    event = Event("ClientLeavesRide", client, leave_ride,
                  extra_info=lambda: str(ride))
    Simulation().schedule(event, delta=ride.duration)


def client_exits_queue(client, ride):
    """
    Event callback: Client loses patience in queue and their state
    changes accordingly

    Immediately schedules the next action through client_decide_next_action
    """
    client.got_on = False
    client.willing_to_queue = False
    client.left_queue(Simulation().time, bad=True)
    ride.remove_from_queue(client)
    client_decide_next_action(client)


def client_leaves_ride(client, ride):
    """
    Event callback: Client leaves ride after successfuly riding and its
    effects are applied, including possible vomiting and crying.

    Immediately schedules the next action through client_decide_next_action
    """
    # Client changes
    client.just_rode = True
    client.got_on = False
    client.rides_ridden.add(ride)
    client.nausea += RIDE_ADULT_NAUSEA_DELTA
    client.energy += RIDE_ADULT_ENERGY_DELTA
    client.hunger += RIDE_ADULT_HUNGER_DELTA
    client.raise_child_nauseas(RIDE_CHILD_NAUSEA_DELTA)
    client.raise_child_energies(RIDE_CHILD_ENERGY_DELTA)
    client.raise_child_hungers(RIDE_CHILD_HUNGER_DELTA)

    # Ride changes
    n_vomit, n_cry = client.vomit_and_cry()
    ride.cry_num[Simulation().time.day] += n_cry
    ride.dirt += RIDE_VOMIT_DIRT * n_vomit
    ride.dirt += RIDE_DIRT_DELTA

    # Next action
    client_decide_next_action(client)
