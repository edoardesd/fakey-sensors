import datetime
import json
import os
import time

import paho.mqtt.client as mqtt
import random
import simpy.rt
import sensor as s

SIM_FACTOR = .01


def on_message(client, userdata, msg):
    print("{} {}", msg.topic, msg.payload.decode("utf-8", "ignore"))


def main():
    #starting_time = time.strftime('%Y-%m-%d %H:%M:%S',  datetime.datetime.now().timestamp())
    starting_time = datetime.datetime.now()
    #print("Simulation started at {}".format(time.strftime("%Y-%m-%d %H:%M:%S", starting_time)))
    print("Simulation started at {}".format(starting_time))
    env = simpy.rt.RealtimeEnvironment(factor=SIM_FACTOR)

    client = mqtt.Client(s.generate_ID())
    client.on_message = on_message

    client.connect(s.BROKER)
    print("Connected.")

    env.process(toggle_as_markov(env, client, starting_time))
    env.process(dim_as_markov(env, client, starting_time))
    env.process(color_as_markow(env, client, starting_time))
    env.run(until=480)


    print("Simulation complete")


def toggle_as_markov(env, _client, _ts):
    global light_status
    while True:
        # update simulation timestamp
        sim_time = _ts + datetime.timedelta(seconds=env.now)
        # set action,topic and draw sojourn time
        if not light_status:
            light_status = True
            action = random.choice(['set_on', 'combo'])
            _topic = s.base_topic + 'action/' + action
            interval = s.draw_on_sojourn(sim_time)
        else:
            light_status = False
            action = 'set_off'
            _topic = s.base_topic + 'action/' + action
            interval = s.draw_off_sojourn(sim_time)

        # execute action and wait until next
        _client.publish(_topic, json.dumps(s.actions[action](sim_time)))

        print("{} - Light is {}".format(sim_time, 'on' if light_status else 'off'))
        print("Will stay {} for {:.1f} real seconds that are {:.4f} sim seconds".format('on' if light_status else 'off', interval, interval*(SIM_FACTOR)))

        yield env.timeout(interval)


def dim_as_markov(env, _client, _ts):
    global light_status
    while True:
        sim_time = _ts + datetime.timedelta(seconds=env.now)

        if light_status:
            action = 'dim'
            _topic = s.base_topic + 'action/' + action
            _client.publish(_topic, json.dumps(s.actions[action](sim_time)))
        else:
            # do nothing if the light is off
            print("Light is off, can't dim")

        # but prepare a new dim event
        interval = s.draw_dim_sojourn(sim_time)
        print("Might change intensity in {:.1f} real seconds that are {:.4f} sim seconds".format(interval, interval*(SIM_FACTOR)))
        yield env.timeout(interval)


def color_as_markow(env, _client, _ts):
    global light_status
    while True:
        sim_time = _ts + datetime.timedelta(seconds=env.now)

        if light_status:
            action = 'color'
            _topic = s.base_topic + 'action/' + action
            _client.publish(_topic, json.dumps(s.actions[action](sim_time)))
        else:
            # do nothing is the light is off
            print("Color is already off, can't change it")

        # but prepare a new color event
        interval = s.draw_color_sojourn(sim_time)
        yield env.timeout(interval)


if __name__ == "__main__":
    sensor = s.Sensor()
    print("+++ PUBLISHER +++")
    name = os.getenv('SENS_NAME', 'bulb0')
    room = os.getenv('SENS_ROOM', 'room0')
    floor = os.getenv('SENS_FLOOR', 'floor0')

    s.get_info()

    light_status = False
    main()
