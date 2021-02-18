import datetime
import json
import paho.mqtt.client as mqtt
import random
import simpy.rt
import thermo_sensor as s


def on_message(client, userdata, msg):
    print("{} {}", msg.topic, msg.payload.decode("utf-8", "ignore"))


def main():
    starting_time = datetime.datetime.now()
    print("Simulation started at {}".format(starting_time))
    env = simpy.rt.RealtimeEnvironment(factor=s.SIM_FACTOR)

    client = mqtt.Client(s.generate_ID())
    client.on_message = on_message

    client.connect(s.BROKER)
    print("Connected.")

    env.process(set_temp_recurrent(env, client, starting_time))
    env.run(until=float(s.SIM_DURATION))

    print("Simulation complete")


def set_temp_recurrent(env, _client, _ts):
    while True:
        # update simulation timestamp
        sim_time = _ts + datetime.timedelta(seconds=env.now)
        action = 'desired_temp'  # note that this action sets the temperature according to a dict. in the sensor class
        _topic = s.base_topic + 'action/' + action
        # execute action and wait until next
        _client.publish(_topic, json.dumps(s.actions[action](sim_time)))
        print("{} - Setting a new desired temp".format(sim_time.replace(microsecond=0)))
        yield env.timeout(3600)


if __name__ == "__main__":
    print("+++ PUBLISHER +++")

    sensor = s.Sensor()
    s.get_info()

    plug_status = False
    main()
