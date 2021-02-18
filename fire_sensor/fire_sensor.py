import os
import random
import string
import datetime
from random import uniform, randrange

COLORS = ['warm_yellow', 'cold_yellow', 'warm_white', 'cold_white', 'red', 'blue', 'green']
BROKER = os.getenv('SENS_BROKER', 'localhost')
PORT = os.getenv('SENS_PORT', 1883)
NAME = os.getenv('SENS_NAME', 'fire0')
ROOM = os.getenv('SENS_ROOM', 'room0')
FLOOR = os.getenv('SENS_FLOOR', 'floor0')
SIM_FACTOR = float(os.getenv('SIM_FACTOR', 0.1))
# for infinite duration use 'inf'
SIM_DURATION = float(os.getenv('SIM_DURATION', 1200))


base_topic = "crazy_building/{}/{}/{}/".format(
    FLOOR, ROOM, NAME)

fire_prob = 0.1


def status_report(timestamp):
    return {"status": {"fire": False},
            "timestamp": str(timestamp)}


def fire_alarm(fire_detected, timestamp):
    return {"status": {"fire": fire_detected},
            "timestamp": str(timestamp)}


def draw_fire():
    return True if uniform(0, 1) <= fire_prob else False


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


actions = {"fire_alarm": fire_alarm}


class Sensor:
    def __init__(self):
        self.client_id = generate_ID()

        self.name = NAME
        self.room = ROOM
        self.floor = FLOOR

        self.broker = BROKER
        self.port = PORT
        self.base_topic = base_topic

        self.topic_passive = {'status_update': {'interval': 300,
                                         'return': self.get_status}}

        self.actions = actions

        self.status = {
            "fire": False}

    def get_status(self, timestamp):
        return {"status": self.status,
                "timestamp": str(timestamp)}

    def store_update(self, _update):
        for key, value in _update.items():
            self.status[key] = value

