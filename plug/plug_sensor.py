import os
import random
import string
from random import randrange, expovariate

COLORS = ['warm_yellow', 'cold_yellow', 'warm_white', 'cold_white', 'red', 'blue', 'green']
BROKER = os.getenv('SENS_BROKER', 'localhost')
PORT = os.getenv('SENS_PORT', 1883)
NAME = os.getenv('SENS_NAME', 'plug0')
ROOM = os.getenv('SENS_ROOM', 'room0')
FLOOR = os.getenv('SENS_FLOOR', 'floor0')
SIM_FACTOR = float(os.getenv('SIM_FACTOR', 0.1))
# for infinite duration use 'inf'
SIM_DURATION = float(os.getenv('SIM_DURATION', 480))

T_PROFILE = os.getenv('T_PROFILE', 'busy')

base_topic = "crazy_building/{}/{}/{}/".format(
    FLOOR, ROOM, NAME)

off_on_trans_rate = 10
on_off_trans_rate = 10



def gen_update_all(timestamp):
    return {"status": {
        "switch": 'ON',
        "dim": random.randrange(0, 100),
        "color": random.choice(COLORS)},
        "timestamp": str(timestamp)}


def turn_off(timestamp):
    return {"status":
                {"switch": 'OFF'},
            "timestamp": str(timestamp)}


def turn_on(timestamp):
    return {"status":
                {"switch": 'ON'},
            "timestamp": str(timestamp)}


def get_info():
    print("Simulation duration: ", SIM_DURATION)
    print("Speed: {}x".format(SIM_FACTOR*100))
    # Not sure about that
    print("\tOne minute in the simulation corresponds to {} seconds in real life.".format(SIM_FACTOR*60))
    print()
    print("Sensor base topic `{}`".format(base_topic))
    print("\tBroker address: {}:{}".format(BROKER, PORT))


def generate_ID():
    return 'CL-' + \
           FLOOR[::len(FLOOR) - 1] + '-' + ROOM[::len(ROOM) - 1] + '-' + \
           NAME + \
           ''.join(random.choice(string.ascii_lowercase) for i in range(randrange(5, 15)))


def draw_off_sojourn(timestamp):
    now = timestamp
    return expovariate(1 / off_on_trans_rate)


def draw_on_sojourn(timestamp):
    now = timestamp
    return expovariate(1 / on_off_trans_rate)


actions = {"set_on": turn_on}


class Sensor:
    def __init__(self):
        self.client_id = generate_ID()

        self.name = NAME
        self.room = ROOM
        self.floor = FLOOR

        self.broker = BROKER
        self.port = PORT
        self.base_topic = base_topic

        self.topic_passive = {'consumption': {'interval': 900,
                                              'return': self.get_consumption},
                              'status': {'interval': 300,
                                         'return': self.get_status}}

        self.actions = actions

        self.status = {
            "switch": 'OFF'}


    def get_consumption(self, timestamp):
        return {"consumption_overall": random.randrange(100, 100000),
                "consumption_last_hour": random.randrange(1, 1000),
                "timestamp": str(timestamp)}

    def get_status(self, timestamp):
        return {"status": self.status,
                "timestamp": str(timestamp)}

    def store_update(self, _update):
        for key, value in _update.items():
            self.status[key] = value

    def get_off_on_rate(self):
        return self.off_on_rate

    def get_on_off_rate(self):
        return self.on_off_rate

