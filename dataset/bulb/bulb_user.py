import datetime
import json
import paho.mqtt.client as mqtt
import random
import simpy.rt
import sensor as s


def on_message(client, userdata, msg):
    print("{} {}", msg.topic, msg.payload.decode("utf-8", "ignore"))


def main():
    starting_time = datetime.datetime.now()
    print("Simulation started at {}".format(starting_time))
    env = simpy.rt.RealtimeEnvironment(factor=s.SIM_FACTOR, strict=False)

    client = mqtt.Client(s.generate_ID())
    client.on_message = on_message

    client.connect(s.BROKER, keepalive=600)
    print("Connected.")

    env.process(toggle_as_markov(env, client, starting_time))
    env.process(dim_as_markov(env, client, starting_time))
    env.process(color_as_markov(env, client, starting_time))
    env.run(until=float(s.SIM_DURATION))

    client.loop_start()
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
            interval = s.draw_on_sojourn(sim_time) * 60
        else:
            light_status = False
            action = 'set_off'
            _topic = s.base_topic + 'action/' + action
            interval = s.draw_off_sojourn(sim_time) * 60

        # execute action and wait until next
        _client.publish(_topic, json.dumps(s.actions[action](sim_time)))

        print("{} - Turning {} the light. Next event in {:.1f} seconds (simulated)".format(sim_time.replace(microsecond=0), 'ON' if light_status else 'OFF', interval*(s.SIM_FACTOR)))

        yield env.timeout(interval)


def dim_as_markov(env, _client, _ts):
    global light_status
    while True:
        sim_time = _ts + datetime.timedelta(seconds=env.now)

        if light_status:
            action = 'dim'
            _topic = s.base_topic + 'action/' + action
            _client.publish(_topic, json.dumps(s.actions[action](sim_time)))
            print("{} - Changing intensity of the light.".format(sim_time.replace(microsecond=0)))
        else:
            # do nothing if the light is off
            # print("Light is off, can't dim")
            pass

        # but prepare a new dim event
        interval = s.draw_dim_sojourn(sim_time) * 60
        #print("Might change intensity in {:.1f} real seconds that are {:.4f} sim seconds".format(interval, interval*(SIM_FACTOR)))
        yield env.timeout(interval)


def color_as_markov(env, _client, _ts):
    global light_status
    while True:
        sim_time = _ts + datetime.timedelta(seconds=env.now)

        if light_status:
            action = 'color'
            _topic = s.base_topic + 'action/' + action
            _client.publish(_topic, json.dumps(s.actions[action](sim_time)))
            print("{} - Changing color of the light.".format(sim_time.replace(microsecond=0)))

        else:
            # do nothing is the light is off
            # print("Color is already off, can't change it")
            pass

        # but prepare a new color event
        interval = s.draw_color_sojourn(sim_time) * 60
        yield env.timeout(interval)


if __name__ == "__main__":
    print("+++ PUBLISHER +++")

    sensor = s.Sensor()
    s.get_info()

    light_status = False
    main()
