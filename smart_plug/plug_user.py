import datetime
import json
import paho.mqtt.client as mqtt
import simpy.rt
import plug_sensor as s


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

    env.process(toggle_as_markov(env, client, starting_time))
    env.run(until=float(s.SIM_DURATION))

    print("Simulation complete")


def toggle_as_markov(env, _client, _ts):
    global plug_status
    while True:
        # update simulation timestamp
        sim_time = _ts + datetime.timedelta(seconds=env.now)
        # set action,topic and draw sojourn time
        if not plug_status:
            plug_status = True
            action = 'set_on'
            _topic = s.base_topic + 'action/' + action
            interval = s.draw_on_sojourn(sim_time) * 60
        else:
            plug_status = False
            action = 'set_off'
            _topic = s.base_topic + 'action/' + action
            interval = s.draw_off_sojourn(sim_time) * 60

        # execute action and wait until next
        _client.publish(_topic, json.dumps(s.actions[action](sim_time)))

        print("{} - Turning {} the light. Next event in {:.1f} seconds (simulated)".format(
            sim_time.replace(microsecond=0), 'ON' if plug_status else 'OFF', interval * (s.SIM_FACTOR)))

        yield env.timeout(interval)


if __name__ == "__main__":
    print("+++ PUBLISHER +++")

    sensor = s.Sensor()
    s.get_info()

    plug_status = False
    main()
