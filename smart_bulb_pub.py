import paho.mqtt.client as mqtt
import threading
import sensor as s
import random


def do_action(_client, _sensor):
    action = random.choice(list(_sensor.actions.keys()))
    print(action)
    _topic = sensor.base_topic + 'action/' + action
    _client.publish(_topic, str(sensor.actions[action]()))
    print("PUB: {}".format(_topic))
    _kwargs = {'_client': _client, '_sensor': _sensor}
    threading.Timer(random.randrange(2, 10), do_action, kwargs=_kwargs).start()


def on_message(client, userdata, msg):
    print("{} {}", msg.topic, msg.payload.decode("utf-8", "ignore"))


def main():
    client = mqtt.Client(sensor.client_id)
    print("Publisher")
    client.on_message = on_message

    print("connecting to the broker", sensor.broker)
    client.connect(sensor.broker)

    #for topic, interval in sensor.topic_passive.items():
    #    client.subscribe(sensor.base_topic + topic)
        # add subscribe log


    #for topic, info in sensor.topic_passive.items():
    #    publish_update(client, topic, info)

    do_action(client, sensor)

    client.loop_start()


if __name__ == "__main__":
    sensor = s.Sensor()
    print("+++ PUBLISHER +++")
    sensor.get_info()
    main()

#while True:
    # parameters
    #hour = datetime.datetime.now()
    #my_hour = int(hour.hour)
    #evening_peak_time = 14
    #night_peak_time = 24
    # myMsg = {"Room":Rooms[0],
    #    "Floors": Floors[0],
    #    "Bulb": Bulbs[0],
    #    "Payload":state
    #    }

    # data_out = json.dumps(myMsg)
    # my_current = datetime.datetime.now()
    # my_hour = int(my_current.hour)

    # if evening_peak_time < my_hour < night_peak_time:
    #    offon=500/3600 #changes from off to on
    #    onoff=480/3600 #changes from on to off
    # else:
    #    offon=6/3600
    #    onoff=5/3600
    # if state==states[1]:
    #    client.publish("apartment/room_1/bulb_1/state", data_out)
    #    time.sleep(numpy.random.exponential(1/offon))
    #    state=states[0]
    # elif state==states[0]:
    #    client.publish("apartment/room_1/bulb_1/state", data_out)
    #    time.sleep(numpy.random.exponential(1/onoff))
    #    state=states[1]
    #pass
#client.loop_stop()
#client.disconnect()
