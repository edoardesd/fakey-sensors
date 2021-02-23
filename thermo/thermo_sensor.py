import os
import random
import string
import datetime
from random import randrange, triangular, gauss

BROKER = os.getenv('SENS_BROKER', 'localhost')
PORT = os.getenv('SENS_PORT', 1883)
NAME = os.getenv('SENS_NAME', 'thermo0')
ROOM = os.getenv('SENS_ROOM', 'room0')
FLOOR = os.getenv('SENS_FLOOR', 'floor0')
SIM_FACTOR = float(os.getenv('SIM_FACTOR', 0.1))
# for infinite duration use 'inf'
SIM_DURATION = float(os.getenv('SIM_DURATION', 480))

base_topic = "crazy_building/{}/{}/{}/".format(
    FLOOR, ROOM, NAME)

hourly_temp = [20, 20, 20, 20, 20, 20, 20, 22, 22, 22, 21, 21, 21, 21, 21, 21,
               21, 21, 21, 21, 21, 21, 20, 20]

temperature_variation_factor = 0.5


def set_temp(timestamp):
    return {"desired_temp": hourly_temp[timestamp.hour]}


def get_info():
    print("Simulation duration: ", SIM_DURATION)
    print("Speed: {}x".format(SIM_FACTOR * 100))
    # Not sure about that
    print("\tOne minute in the simulation corresponds to {} seconds in real life.".format(SIM_FACTOR * 60))
    print()
    print("Sensor base topic `{}`".format(base_topic))
    print("\tBroker address: {}:{}".format(BROKER, PORT))


def generate_ID():
    return 'CL-' + \
           FLOOR[::len(FLOOR) - 1] + '-' + ROOM[::len(ROOM) - 1] + '-' + \
           NAME + \
           ''.join(random.choice(string.ascii_lowercase) for i in range(randrange(5, 15)))


actions = {"desired_temp": set_temp}


class Sensor:
    def __init__(self):
        self.client_id = generate_ID()

        self.name = NAME
        self.room = ROOM
        self.floor = FLOOR

        self.broker = BROKER
        self.port = PORT
        self.base_topic = base_topic
        fifteen_minutes = 15*60;
        self.topic_passive = {'status': {'interval': fifteen_minutes,
                                         'return': self.get_status}}

        self.actions = actions

        self.status = {
            "desired_temp": 22,
            "current_temp": 19,
            "humidity": 50}

    def temperature_simulation_engine(self):
        drift_direction = -1 if self.status["desired_temp"] - self.status["current_temp"] < 0 else 1
        self.status["current_temp"] = self.status["current_temp"] + \
                                      drift_direction *\
                                      max(abs(self.status["desired_temp"] - self.status["current_temp"]) *
                                          temperature_variation_factor, temperature_variation_factor) + gauss(0, 0.3)

        self.status["humidity"] = triangular(30, 70, 50)

    def get_status(self, timestamp):
        self.temperature_simulation_engine()
        return {"status": self.status,
                "timestamp": str(timestamp)}

    def store_update(self, _update):
        for key, value in _update.items():
            self.status[key] = value
