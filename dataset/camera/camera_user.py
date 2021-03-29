import datetime
import json
import paho.mqtt.client as mqtt
import simpy.rt
import camera as c


def on_message(client, userdata, msg):
    print("{} {}", msg.topic, msg.payload.decode("utf-8", "ignore"))


def main():
    starting_time = datetime.datetime.now()
    print("Simulation started at {}".format(starting_time))
    env = simpy.rt.RealtimeEnvironment(factor=c.SIM_FACTOR, strict=False)

    client = mqtt.Client(c.generate_ID())
    client.on_message = on_message

    client.connect(c.BROKER, keepalive=600)
    print("Connected.")

    env.process(toggle_as_markov(env, client, starting_time))
    env.run(until=float(c.SIM_DURATION))

    client.loop_start()
    print("Simulation complete")


def toggle_as_markov(env, _client, _ts):
    global camera_status
    while True:
        # update simulation timestamp
        sim_time = _ts + datetime.timedelta(seconds=env.now)

        _action = 'camera_fps'
        _topic = c.base_topic + 'action/' + _action
        # one simulation hour = 60*60
        _interval = 60*60
        # execute action and wait until next
        _client.publish(_topic, json.dumps(c.actions[_action](sim_time)))

        print("{} - Camera changed status, next event in {} seconds (real time = {} seconds)".format(sim_time, _interval, _interval*c.SIM_FACTOR))

        yield env.timeout(_interval)


if __name__ == "__main__":
    print("+++ PUBLISHER +++")

    sensor = c.Camera()
    c.get_info()

    camera_status = False
    main()
