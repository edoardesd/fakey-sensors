import base64
import os
import random
import string
from random import randrange, expovariate
from os import walk

BROKER = os.getenv('SENS_BROKER', 'localhost')
PORT = os.getenv('SENS_PORT', 1883)
NAME = os.getenv('SENS_NAME', 'tv0')
ROOM = os.getenv('SENS_ROOM', 'room0')
FLOOR = os.getenv('SENS_FLOOR', 'floor0')
SIM_FACTOR = float(os.getenv('SIM_FACTOR', 0.01))
# for infinite duration use 'inf'
SIM_DURATION = float(os.getenv('SIM_DURATION', 'inf'))

T_PROFILE = os.getenv('T_PROFILE', 'busy')

base_topic = "crazy_building/{}/{}/{}/".format(
    FLOOR, ROOM, NAME)

off_on_trans_rates = {"busy": 10, "steady": 23}
on_off_trans_rates = {'busy': 10, 'steady': 22}
channel_trans_rates = {'busy': 5, 'steady': 22}
volume_trans_rates = {'busy': 5, 'steady': 22}

hourly_rates = [2.06, 1.74, 2.20, 6.47, 3.00, 2.47, 2.20, 3.74, 4.06, 2.32, 2.33, 2.08, 2.08, 2.33, 8.32, 4.06,
                9.74, 1.20, 6.47, 3.00, 6.47, 1.20, 1.74, 2.06]

channels_interval = [0, 25, 25, 50, 50, 25, 55, 15, 43, 20, 35, 45]


def change_volume(timestamp):
    return {"status": {"volume": random.randrange(5, 20)},
            "timestamp": str(timestamp)}


def change_channel(timestamp):
    return {"status": {"channel": random.randrange(1, 10)},
            "timestamp": str(timestamp)}


def turn_off(timestamp):
    return {"status":
                {"interval": 0,
                 "switch": 'OFF',
                 "channel": 0,
                 "volume": 0},
            "timestamp": str(timestamp)}


def turn_on(timestamp):
    return {"status":
                {"interval": 5,
                 "switch": 'ON',
                 "channel": random.randrange(1, 10),
                 "volume": random.randrange(8, 20)},
            "timestamp": str(timestamp)}


def draw_channel_sojourn(timestamp):
    now = timestamp
    return random.expovariate(1 / (channel_trans_rates[T_PROFILE] * hourly_rates[now.hour]))


def draw_off_sojourn(timestamp):
    now = timestamp
    return random.expovariate(1 / (off_on_trans_rates[T_PROFILE] * hourly_rates[now.hour]))


def draw_on_sojourn(timestamp):
    now = timestamp
    return random.expovariate(1 / (on_off_trans_rates[T_PROFILE] * hourly_rates[now.hour]))


def draw_volume_sojourn(timestamp):
    now = timestamp
    return random.expovariate(1 / (volume_trans_rates[T_PROFILE] * hourly_rates[now.hour]))


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


actions = {"volume": change_volume,
           "channel": change_channel,
           "turn_on": turn_on,
           "turn_off": turn_off}

draw_sojourn = {'volume': draw_volume_sojourn,
                'channel': draw_channel_sojourn}


class TV:
    def __init__(self):
        self.client_id = generate_ID()

        self.name = NAME
        self.room = ROOM
        self.floor = FLOOR

        self.broker = BROKER
        self.port = PORT
        self.base_topic = base_topic

        self.channel = 0
        self.status = {"interval": self.channel,
                       "switch": 'OFF',
                       "volume": 0,
                       "channel": self.channel}

        self.topic_passive = {'consumption': {'interval': 10000,
                                              'return': self.get_consumption}}

        self.topic_active = {'stream': {'interval': self.status["interval"],
                                        'return': self.get_video}}
        self.actions = actions

    def get_rate(self):
        self.channel = self.status["channel"]
        self.status["interval"] = channels_interval[self.channel]
        return self.status

    def get_consumption(self, timestamp):
        return {"consumption_overall": random.randrange(90, 5000),
                "consumption_last_hour": random.randrange(10, 275),
                "timestamp": str(timestamp)}

    def get_status(self, timestamp):
        return {"status": self.status,
                "timestamp": str(timestamp)}

    def get_video(self, timestamp):
        dir_path = os.path.dirname(os.path.realpath(__file__)) + "/camera_frames/"
        _, _, filenames = next(walk(dir_path))
        with open(dir_path + random.choice(filenames), "rb") as imageFile:
            image_str = str(base64.b64encode(imageFile.read()))
            return {"status": {"frame": image_str},
                    "timestamp": str(timestamp)}

    def store_update(self, _update):
        for key, value in _update.items():
            self.status[key] = value
