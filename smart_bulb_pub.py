import json
import os
import time

import paho.mqtt.client as mqtt
import threading
import sensor as s
import random


#def do_toogle(self):
#    if "ON" in self.status["switch"]:
#        self.status["switch"] = "OFF"
#    if "OFF" in self.status["switch"]:
#        self.status["switch"] = "ON"




def do_action(_client):
    action = random.choice(list(s.actions.keys()))
    _topic = s.base_topic + 'action/' + action
    _client.publish(_topic, json.dumps(s.actions[action]()))
    print("PUB: {} {}".format(_topic, json.dumps(s.actions[action]())))
    _kwargs = {'_client': _client}
    threading.Timer(random.randrange(2, 10), do_action, kwargs=_kwargs).start()


def dim_as_markov(_client):
    global isOn
    if isOn:
        action = 'dim'
        _topic = s.base_topic + 'action/' + action
        _client.publish(_topic, json.dumps(s.actions[action]()))
    else:
        # do nothing if the light is off
        print("Light is off, can't dim")

    # but prepare a new dim event
    interval = s.draw_dim_sojourn()
    print("Might change intensity in {} minutes".format(interval / 60))
    threading.Timer(interval, dim_as_markov, [_client]).start()


def toggle_as_markov(_client):
    global isOn
    # set action,topic and draw sojourn time
    if not isOn:
        isOn = True
        action = random.choice(['set_on', 'combo'])
        _topic = s.base_topic + 'action/' + action
        interval = s.draw_on_sojourn()
        print("Will stay on for " + str(interval/60) + " minutes")
    else:
        isOn = False
        action = 'set_off'
        _topic = s.base_topic + 'action/' + action
        interval = s.draw_off_sojourn()
        print("Will stay off for " + str(interval/60) + " minutes")

    # execute action and schedule next
    _client.publish(_topic, json.dumps(s.actions[action]()))
    threading.Timer(interval, toggle_as_markov, [_client]).start()


def on_message(client, userdata, msg):
    print("{} {}", msg.topic, msg.payload.decode("utf-8", "ignore"))


def main():
    client = mqtt.Client(s.generate_ID())
    client.on_message = on_message

    client.connect(s.BROKER)
    print("Connected.")

    # periodic update
    #do_action(client)

    client.loop_start()

    # on off toggling
    toggle_as_markov(client)
    dim_as_markov(client)


if __name__ == "__main__":
    sensor = s.Sensor()
    print("+++ PUBLISHER +++")
    name = os.getenv('SENS_NAME', 'bulb0')
    room = os.getenv('SENS_ROOM', 'room0')
    floor = os.getenv('SENS_FLOOR', 'floor0')

    isOn = False

    s.get_info()

    main()

#while True:
    # parameters
    #hour = datetime.datetime.now()
    #my_hour = int(hour.hour)
    #evening_peak_time = 14
    #night_peak_time = 24
    # myMsg = {"Room":Rooms[0],
    #    "Floors": Floors[0],
    #    "Bulb": Bulbs[0],
    #    "Payload":state
    #    }

    # data_out = json.dumps(myMsg)
    # my_current = datetime.datetime.now()
    # my_hour = int(my_current.hour)

    # if evening_peak_time < my_hour < night_peak_time:
    #    offon=500/3600 #changes from off to on
    #    onoff=480/3600 #changes from on to off
    # else:
    #    offon=6/3600
    #    onoff=5/3600
    # if state==states[1]:
    #    client.publish("apartment/room_1/bulb_1/state", data_out)
    #    time.sleep(numpy.random.exponential(1/offon))
    #    state=states[0]
    # elif state==states[0]:
    #    client.publish("apartment/room_1/bulb_1/state", data_out)
    #    time.sleep(numpy.random.exponential(1/onoff))
    #    state=states[1]
    #pass
#client.loop_stop()
#client.disconnect()
