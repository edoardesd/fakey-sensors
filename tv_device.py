import datetime
import json
import paho.mqtt.client as mqtt
import simpy.rt

import smart_tv as tv


def publish_update(_client, _topic, _info):
    while True:
        sim_time = starting_time + datetime.timedelta(seconds=env.now)
        _client.publish(sensor.base_topic + _topic, json.dumps(_info['return'](sim_time)))
        print("{} - Publish on topic `{}`.".format(sim_time.replace(microsecond=0), _topic))

        yield env.timeout(_info['interval'])


def publish_frame(_client, _topic, _info):
    while True:
        sim_time = starting_time + datetime.timedelta(seconds=env.now)
        interval = sensor.get_rate()["interval"]
        print(interval)
        if interval == 0:
            yield env.process(stop())

        _client.publish(sensor.base_topic + _topic, json.dumps(_info['return'](sim_time)))
        print("{} - Publish on topic `{}`.".format(sim_time.replace(microsecond=0), _topic))

        yield env.timeout(interval)


def stop():
    print("Television turned OFF")
    while sensor.get_rate()["interval"] == 0:
        pass
    print("Turning ON the telly")
    yield env.timeout(1)


def on_message(client, userdata, msg):
    print("Received {} {}".format(msg.topic, msg.payload.decode("utf-8", "ignore")))
    sensor.store_update(dict(json.loads(msg.payload.decode("utf-8")))["status"])


def main():
    client = mqtt.Client(sensor.client_id)
    client.on_message = on_message

    print("connecting to the broker", sensor.broker)
    client.connect(sensor.broker)

    for topic in sensor.actions.keys():
        client.subscribe(sensor.base_topic + 'action/' + topic)
        # add subscriber log

    for topic, info in sensor.topic_passive.items():
        env.process(publish_update(client, topic, info))

    env.process(publish_frame(client, 'stream', sensor.topic_active['stream']))

    # subscriber remains active
    client.loop_start()

    # start the simulation
    env.run(until=float(tv.SIM_DURATION))


if __name__ == "__main__":
    print("+++ SUBSCRIBER +++")
    starting_time = datetime.datetime.now()
    print("Simulation started at {}".format(starting_time))
    env = simpy.rt.RealtimeEnvironment(factor=tv.SIM_FACTOR, strict=False)

    sensor = tv.TV()

    tv.get_info()
    main()
