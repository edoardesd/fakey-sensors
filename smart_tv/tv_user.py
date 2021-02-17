import datetime
import json
import random

import paho.mqtt.client as mqtt
import simpy.rt
import smart_tv as tv


def on_message(client, userdata, msg):
    print("{} {}", msg.topic, msg.payload.decode("utf-8", "ignore"))


def on_publish(client, userdata, mid):
    print("on_publish, mid {}".format(mid))


def main():
    starting_time = datetime.datetime.now()
    print("Simulation started at {}".format(starting_time))
    env = simpy.rt.RealtimeEnvironment(factor=tv.SIM_FACTOR, strict=False)

    client = mqtt.Client(tv.generate_ID())
    client.on_message = on_message
    client.on_publish = on_publish

    client.connect(tv.BROKER)
    print("Connected.")

    env.process(toggle_as_markov(env, client, starting_time))
    env.process(telly_as_markov(env, client, starting_time))
    env.run(until=float(tv.SIM_DURATION))

    print("Simulation complete")


def toggle_as_markov(env, _client, _ts):
    global tv_status
    while True:
        # update simulation timestamp
        sim_time = _ts + datetime.timedelta(seconds=env.now)
        # set action,topic and draw sojourn time
        if not tv_status:
            tv_status = True
            action = 'turn_on'
            _topic = tv.base_topic + 'action/' + action
            interval = tv.draw_on_sojourn(sim_time) * 60
        else:
            tv_status = False
            action = 'turn_off'
            _topic = tv.base_topic + 'action/' + action
            interval = tv.draw_off_sojourn(sim_time) * 60

        print("{} - Turning {} the telly on topic {}. Next event in {:.1f} seconds (simulated)".format(
            sim_time.replace(microsecond=0), 'ON' if tv_status else 'OFF', _topic, interval * (tv.SIM_FACTOR)))

        # execute action and wait until next
        _client.publish(_topic, json.dumps(tv.actions[action](sim_time)), qos=1)

        yield env.timeout(interval)


def telly_as_markov(env, _client, _ts):
    global tv_status
    while True:
        sim_time = _ts + datetime.timedelta(seconds=env.now)

        if tv_status:
            action = random.choice(['volume', 'channel'])
            _topic = tv.base_topic + 'action/' + action
            print("{} - Changing the {}.".format(sim_time.replace(microsecond=0), action))
            _client.publish(_topic, json.dumps(tv.actions[action](sim_time)))
        else:
            # do nothing if the tv is off
            # print("Telly is off, can't do anything")
            pass

        interval = tv.draw_sojourn[action](sim_time) * 60
        #print("Might change {} in {:.1f} real seconds that are {:.4f} sim seconds".format(action, interval, interval*(SIM_FACTOR)))
        yield env.timeout(interval)


if __name__ == "__main__":
    print("+++ PUBLISHER +++")

    sensor = tv.TV()
    tv.get_info()

    tv_status = False
    main()
