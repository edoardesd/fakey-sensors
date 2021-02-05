import time
import os
import random
import string

from random import randrange


class Sensor:
    def __init__(self):
        self.name = os.getenv('SENS_NAME', 'bulb0')
        self.room = os.getenv('SENS_ROOM', 'room0')
        self.floor = os.getenv('SENS_FLOOR', 'floor0')

        self.base_topic = "crazy_building/{}/{}/{}/".format(
            self.floor, self.room, self.name)

        self.broker = os.getenv('SENS_BROKER', 'localhost')
        self.port = os.getenv('SENS_PORT', 1883)

        self.topic_passive = {'consumption': {'interval': 20,
                                              'return': self.get_consumption},
                              'status': {'interval': 10,
                                         'return': self.get_status}}

        self.switch = 'OFF'
        self.dim = 0
        self.color = None

        self.actions = {'switch': ['ON', 'OFF'],
                        'dim': [range(0, 100)],
                        'color': ['warm_yellow', 'cold_yellow', 'warm_white', 'cold_withe', 'red', 'blue', 'green']}

        self.seconds_on = 0

        self.client_id = self.generate_ID()

    def generate_ID(self):
        return 'CL-' + \
               self.floor[::len(self.floor) - 1] + '-' + self.room[::len(self.room) - 1] + '-' + \
               self.name + \
               ''.join(random.choice(string.ascii_lowercase) for i in range(randrange(5, 15)))

    def get_info(self):
        print("Sensor name:", self.name)
        print("\tRoom:", self.room)
        print("\tFoor:", self.floor)
        print()
        print("\tBroker address: {}:{}".format(self.broker, self.port))

    def get_consumption(self):
        return {'consumption_overall': random.randrange(100, 100000),
                'consumption_last_hour': random.randrange(1, 1000),
                'timestamp': time.time()}

    def get_status(self):
        return {'switch': self.switch,
                'dim': self.dim,
                'color': self.color,
                'timestamp': time.time()
                }

    def turn_off(self):
        self.switch = 'OFF',
        self.dim = 0,
        self.color = None

    def turn_on(self):
        self.switch = 'ON',
        self.dim = 50
        self.color = self.actions[0]
