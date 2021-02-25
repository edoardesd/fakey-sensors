import datetime
import json
import paho.mqtt.client as mqtt
import simpy.rt

import thermo_sensor as s


def publish_update(env, _client, _ts, _topic, _info):
    while True:
        sim_time = _ts + datetime.timedelta(seconds=env.now)
        _client.publish(sensor.base_topic + _topic, json.dumps(_info['return'](sim_time)))
        print("{} - Publish on topic `{}`.".format(sim_time.replace(microsecond=0), _topic))
        yield env.timeout(_info['interval'])


def on_message(client, userdata, msg):
    print("Received {} {}".format(msg.topic, msg.payload.decode("utf-8", "ignore")))
    sensor.store_update(dict(json.loads(msg.payload.decode("utf-8"))))


def main():
    starting_time = datetime.datetime.now()
    print("Simulation started at {}".format(starting_time))
    env = simpy.rt.RealtimeEnvironment(factor=s.SIM_FACTOR, strict=False)

    client = mqtt.Client(sensor.client_id)
    client.on_message = on_message

    print("connecting to the broker", sensor.broker)
    client.connect(sensor.broker, keepalive=600)

    for topic in sensor.actions.keys():
        client.subscribe(sensor.base_topic + 'action/' + topic)
        # add subscriber log

    for topic, info in sensor.topic_passive.items():
        env.process(publish_update(env, client, starting_time, topic, info))

    # subscriber remains active
    client.loop_start()

    # start the simulation
    env.run(until=float(s.SIM_DURATION))


if __name__ == "__main__":
    print("+++ SUBSCRIBER +++")
    sensor = s.Sensor()

    s.get_info()
    main()
