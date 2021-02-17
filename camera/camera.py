import base64
import os
import random
import string
from random import randrange, expovariate
from os import walk

BROKER = os.getenv('SENS_BROKER', 'localhost')
PORT = os.getenv('SENS_PORT', 1883)
NAME = os.getenv('SENS_NAME', 'camera0')
ROOM = os.getenv('SENS_ROOM', 'room0')
FLOOR = os.getenv('SENS_FLOOR', 'floor0')
SIM_FACTOR = os.getenv('SIM_FACTOR', 0.01)
# for infinite duration use 'inf'
SIM_DURATION = os.getenv('SIM_DURATION', 'inf')

T_PROFILE = os.getenv('T_PROFILE', 'steady')

base_topic = "crazy_building/{}/{}/{}/".format(
    FLOOR, ROOM, NAME)

FPS = {"HIGH": 1, "LOW": 10, "OFF": 0}
hourly_rates = {
    "busy": ['HIGH', 'HIGH', 'HIGH', 'HIGH', 'HIGH', 'HIGH', 'HIGH', 'HIGH', 'HIGH', 'LOW', 'LOW', 'LOW', 'LOW',
             'HIGH', 'HIGH', 'HIGH', 'LOW', 'LOW', 'LOW', 'HIGH', 'HIGH', 'HIGH', 'HIGH', 'HIGH'],
    "steady": ['HIGH', 'HIGH', 'HIGH', 'HIGH', 'HIGH', 'LOW', 'HIGH', 'LOW', 'OFF', 'LOW', 'OFF', 'HIGH', 'LOW',
               'LOW', 'LOW', 'OFF', 'OFF', 'LOW', 'LOW', 'LOW', 'LOW', 'LOW', 'HIGH', 'HIGH']
}


def mod_camera(timestamp):
    return {"status": {"interval": FPS[hourly_rates[T_PROFILE][int(timestamp.hour)]]},
            "timestamp": str(timestamp)}


def get_info():
    print("Simulation duration: ", SIM_DURATION)
    print("Speed: {}x".format(SIM_FACTOR * 100))
    # Not sure about that
    print("\tOne minute in the simulation corresponds to {} seconds in real life.".format(SIM_FACTOR * 60))
    print()
    print("Sensor base topic `{}`".format(base_topic))
    print("\tBroker address: {}:{}".format(BROKER, PORT))
    print()


def generate_ID():
    return 'CL-' + \
           FLOOR[::len(FLOOR) - 1] + '-' + ROOM[::len(ROOM) - 1] + '-' + \
           NAME + \
           ''.join(random.choice(string.ascii_lowercase) for i in range(randrange(5, 15)))


actions = {"camera_fps": mod_camera}


class Camera:
    def __init__(self):
        self.client_id = generate_ID()

        self.name = NAME
        self.room = ROOM
        self.floor = FLOOR

        self.broker = BROKER
        self.port = PORT
        self.base_topic = base_topic

        self.status = {"interval": FPS["LOW"],
                       "old": FPS["OFF"]}

        self.topic_passive = {'consumption': {'interval': 10000,
                                              'return': self.get_consumption}}

        self.topic_active = {'stream': {'interval': self.status["interval"],
                                        'return': self.get_pic}}
        self.actions = actions

    def get_rate(self):
        return self.status

    def get_consumption(self, timestamp):
        return {"consumption_overall": random.randrange(600, 500000),
                "consumption_last_hour": random.randrange(5, 9000),
                "timestamp": str(timestamp)}

    def get_status(self, timestamp):
        return {"status": self.status,
                "timestamp": str(timestamp)}

    def get_pic(self, timestamp):
        dir_path = os.path.dirname(os.path.realpath(__file__)) + "/camera_frames/"
        _, _, filenames = next(walk(dir_path))
        with open(dir_path + random.choice(filenames), "rb") as imageFile:
            image_str = str(base64.b64encode(imageFile.read()))
            return {"status": {"frame": image_str},
                    "timestamp": str(timestamp)}

    def store_update(self, _update):
        self.status['old'] = self.status['interval']
        for key, value in _update.items():
            self.status[key] = value
