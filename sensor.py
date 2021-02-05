import time
import os
import random
import string

from random import randrange


COLORS = ['warm_yellow', 'cold_yellow', 'warm_white', 'cold_withe', 'red', 'blue', 'green']

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

        self.actions = {'switch': self.toogle,
                        'set_on': self.turn_on,
                        'set_off': self.turn_off,
                        'dim': self.set_intensity,
                        'color': self.set_color,
                        'combo': self.update_all}

        self.seconds_on = 0

        self.client_id = self.generate_ID()

    def set_intensity(self):
        new_dim = random.randrange(0, 100)
        if self.dim == new_dim:
            return self.set_intensity()
        else:
            self.dim = new_dim
            return {'dim': self.dim,
                    'timestamp': time.time()}


    def set_color(self):
        new_color = random.choice(COLORS)
        if self.color == new_color:
            return self.set_color()
        else:
            self.color = new_color
            return {'color': self.color,
                    'timestamp': time.time()}

    def update_all(self):
        self.switch = 'ON'
        self.set_intensity()
        self.set_color()

        return self.get_status()

    def toogle(self):
        if 'ON' in self.switch:
            self.switch = 'OFF'
        if 'OFF' in self.switch:
            self.switch = 'ON'

        return {'switch': self.switch,
                'timestamp': time.time()
                }

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
        self.switch = 'OFF'
        self.dim = 0
        self.color = None

        return self.get_status()

    def turn_on(self):
        self.switch = 'ON'
        self.dim = 50
        self.color = COLORS[0]

        return self.get_status()
