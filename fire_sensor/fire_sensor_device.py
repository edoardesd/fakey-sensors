import datetime
import json
import paho.mqtt.client as mqtt
import simpy.rt

import fire_sensor as s


def publish_update(env, _client, _ts, _topic, _info):
    global fire_detected
    while True:
        if not fire_detected:
            if s.draw_fire():
                fire_detected = 2
                sim_time = _ts + datetime.timedelta(seconds=env.now)
                print("{} - Fire was just detected...".format(sim_time.replace(microsecond=0)))
                continue
            sim_time = _ts + datetime.timedelta(seconds=env.now)
            _client.publish(sensor.base_topic + _topic, json.dumps(_info['return'](sim_time)))
            print("{} - Publish on topic `{}`.".format(sim_time.replace(microsecond=0), _topic))
            yield env.timeout(_info['interval'])
        else:
            # publish fire alarm each 30 seconds for 5 minutes, i.e. 10 times
            sim_time = _ts + datetime.timedelta(seconds=env.now)
            fire_topic = s.base_topic + 'action/' + 'fire_alarm'
            _client.publish(fire_topic, json.dumps(s.actions['fire_alarm'](True, sim_time)))
            print("{} - Publish fire detected on on topic `{}`.".format(sim_time.replace(microsecond=0), fire_topic))
            fire_detected -= 1
            yield env.timeout(30)
            if not fire_detected:
                print("{} - Fire ceased...".format(sim_time.replace(microsecond=0)))
                _client.publish(fire_topic, json.dumps(s.actions['fire_alarm'](False, sim_time)))
                print(
                    "{} - Publish fire ceased on on topic `{}`.".format(sim_time.replace(microsecond=0), fire_topic))
                yield env.timeout(_info['interval'])


def on_message(client, userdata, msg):
    print("Received {} {}".format(msg.topic, msg.payload.decode("utf-8", "ignore")))
    sensor.store_update(dict(json.loads(msg.payload.decode("utf-8")))["status"])


def main():
    starting_time = datetime.datetime.now()
    print("Simulation started at {}".format(starting_time))
    env = simpy.rt.RealtimeEnvironment(factor=s.SIM_FACTOR)

    client = mqtt.Client(sensor.client_id)
    client.on_message = on_message

    print("connecting to the broker", sensor.broker)
    client.connect(sensor.broker)

    for topic in sensor.actions.keys():
        client.subscribe(sensor.base_topic + 'action/' + topic)
        # add subscriber log

    processes = {}

    for topic, info in sensor.topic_passive.items():
        processes[topic] = env.process(publish_update(env, client, starting_time, topic, info,))

    # subscriber remains active
    client.loop_start()

    # start the simulation
    env.run(until=float(s.SIM_DURATION))


if __name__ == "__main__":
    print("+++ SUBSCRIBER +++")
    sensor = s.Sensor()
    fire_detected = 0

    s.get_info()
    main()
