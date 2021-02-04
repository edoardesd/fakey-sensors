import time
import paho.mqtt.client as mqtt
import datetime
import os
import random
import string
import threading
import json
from time import localtime, strftime, sleep

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

        self.topic_passive = {'consumption': 20,
                              'status': 10}

        self.status = {'switch': 'OFF',
                       'dim': 0,
                       'color': None}

        self.actions = {'switch': ['ON', 'OFF'],
                        'dim': [range(0, 100)],
                        'color': ['warm_yellow', 'cold_yellow', 'warm_white', 'cold_withe', 'red', 'blue', 'green']}

        self.seconds_on = 0

        self.consumption = 28123

        self.client_id = self.generate_ID()

    def generate_ID(self):
        return 'CL-' + \
               self.floor[::len(self.floor)-1] + '-' + self.room[::len(self.room)-1] + '-' + \
               self.name +\
               ''.join(random.choice(string.ascii_lowercase) for i in range(randrange(5, 15)))


    def get_info(self):
        print("Sensor name:", self.name)
        print("\tRoom:", self.room)
        print("\tFoor:", self.floor)
        print()
        print("\tBroker address: {}:{}".format(self.broker, self.port))


#parameters
hour = datetime.datetime.now()
my_hour = int(hour.hour)
evening_peak_time = 14
night_peak_time = 24

def publish_status(_client):
    _client.publish(sensor.base_topic+"status", str(sensor.status))
    threading.Timer(5, publish_status, kwargs={'_client': _client}).start()

def publish_consumption(_client):
    _client.publish(sensor.base_topic+"consumption", str(sensor.consumption))
    threading.Timer(5, publish_consumption(), kwargs={'_client': _client}).start()


def on_message(client, userdata, msg):
    print("{} {}", msg.topic, msg.payload.decode("utf-8","ignore"))


def main():
    client = mqtt.Client(sensor.client_id)
    print(client)
    client.on_message = on_message

    print("connecting to the broker", sensor.broker)
    client.connect(sensor.broker)

    for topic, interval in sensor.topic_passive.items():
        print(topic, interval)
        client.subscribe(sensor.base_topic + topic)
        # add subscribe log


    publish_status(client)
    #publish_consumption()

    client.loop_start()


if __name__ == "__main__":
    sensor = Sensor()
    sensor.get_info()
    main()





while True:
    #myMsg = {"Room":Rooms[0],
    #    "Floors": Floors[0],
    #    "Bulb": Bulbs[0],
    #    "Payload":state
    #    }

    #data_out = json.dumps(myMsg)
    #my_current = datetime.datetime.now()
    #my_hour = int(my_current.hour)

    #if evening_peak_time < my_hour < night_peak_time:
    #    offon=500/3600 #changes from off to on
    #    onoff=480/3600 #changes from on to off
    #else:
    #    offon=6/3600
    #    onoff=5/3600
    #if state==states[1]:
    #    client.publish("apartment/room_1/bulb_1/state", data_out)
    #    time.sleep(numpy.random.exponential(1/offon))
    #    state=states[0]
    #elif state==states[0]:
    #    client.publish("apartment/room_1/bulb_1/state", data_out)
    #    time.sleep(numpy.random.exponential(1/onoff))
    #    state=states[1]
    pass
client.loop_stop()
client.disconnect()