import datetime
import json
import os
import paho.mqtt.client as mqtt
import simpy.rt

import camera as c


def publish_update(env, _client, _ts, _topic, _info, _sensor):
    while True:
        sim_time = _ts + datetime.timedelta(seconds=env.now)
        _client.publish(sensor.base_topic + _topic, json.dumps(_info['return'](sim_time)))
        print("{} - Publish on topic `{}`.".format(sim_time.replace(microsecond=0), _topic))
        _interval = _sensor.get_rate()["interval"]
        yield env.timeout(_interval)


def on_message(client, userdata, msg):
    print("Received {} {}".format(msg.topic, msg.payload.decode("utf-8", "ignore")))
    sensor.store_update(dict(json.loads(msg.payload.decode("utf-8")))["status"])



def main():
    starting_time = datetime.datetime.now()
    print("Simulation started at {}".format(starting_time))
    env = simpy.rt.RealtimeEnvironment(factor=c.SIM_FACTOR)

    client = mqtt.Client(sensor.client_id)
    client.on_message = on_message

    print("connecting to the broker", sensor.broker)
    client.connect(sensor.broker)

    for topic in sensor.actions.keys():
        client.subscribe(sensor.base_topic + 'action/' + topic)
        # add subscriber log

    for topic, info in sensor.topic_passive.items():
        env.process(publish_update(env, client, starting_time, topic, info, sensor))

    # subscriber remains active
    client.loop_start()

    # start the simulation
    env.run(until=float(c.SIM_DURATION))


if __name__ == "__main__":
    print("+++ SUBSCRIBER +++")
    sensor = c.Camera()

    c.get_info()
    main()
