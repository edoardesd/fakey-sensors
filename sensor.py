import time
import os
import random
import string

from random import randrange

COLORS = ['warm_yellow', 'cold_yellow', 'warm_white', 'cold_white', 'red', 'blue', 'green']
BROKER = os.getenv('SENS_BROKER', 'localhost')
PORT = os.getenv('SENS_PORT', 1883)
NAME = os.getenv('SENS_NAME', 'bulb0')
ROOM = os.getenv('SENS_ROOM', 'room0')
FLOOR = os.getenv('SENS_FLOOR', 'floor0')

base_topic = "crazy_building/{}/{}/{}/".format(
    FLOOR, ROOM, NAME)


def gen_intensity():
    return {"status": {"dim": random.randrange(0, 100)},
            "timestamp": time.time()}


def gen_color():
    return {"status": {"color": random.choice(COLORS)},
            "timestamp": time.time()}


def gen_toogle():
    return {"status": {"switch": random.choice(["ON", "OFF"])},
            "timestamp": time.time()}


def gen_update_all():
    return {"status": {
        "switch": 'ON',
        "dim": random.randrange(0, 100),
        "color": random.choice(COLORS)},
        "timestamp": time.time()}


def turn_off():
    return {"status":
                {"switch": 'OFF',
                 "dim": 0,
                 "color": None},
            "timestamp": time.time()}


def turn_on():
    return {"status":
                {"switch": 'ON',
                 "dim": 50,
                 "color": COLORS[0]},
            "timestamp": time.time()}


def get_info():
    print("Sensor name:", NAME)
    print("\tRoom:", ROOM)
    print("\tFoor:", FLOOR)
    print()
    print("\tBroker address: {}:{}".format(BROKER, PORT))


def generate_ID():
    return 'CL-' + \
           FLOOR[::len(FLOOR) - 1] + '-' + ROOM[::len(ROOM) - 1] + '-' + \
           NAME + \
           ''.join(random.choice(string.ascii_lowercase) for i in range(randrange(5, 15)))


actions = {"switch": gen_toogle,
           "set_on": turn_on,
           "set_off": turn_off,
           "dim": gen_intensity,
           "color": gen_color,
           "combo": gen_update_all}


class Sensor:
    def __init__(self):
        self.client_id = generate_ID()

        self.name = NAME
        self.room = ROOM
        self.floor = FLOOR

        self.broker = BROKER
        self.port = PORT
        self.base_topic = base_topic

        self.topic_passive = {'consumption': {'interval': 20,
                                              'return': self.get_consumption},
                              'status': {'interval': 10,
                                         'return': self.get_status}}

        self.actions = actions

        self.status = {
            "switch": 'OFF',
            "dim": 0,
            "color": None}

    def get_consumption(self):
        return {"consumption_overall": random.randrange(100, 100000),
                "consumption_last_hour": random.randrange(1, 1000),
                "timestamp": time.time()}

    def get_status(self):
        return {"status": self.status,
                "timestamp": time.time()}

    def store_update(self, _update):
        for key, value in _update.items():
            self.status[key] = value
