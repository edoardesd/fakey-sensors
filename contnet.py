"""
Example topology with two containers (d1, d2),
two switches, and one controller:

          - (c)-
            |
(broker) - (s1) - (device_0)
         - s2 - device_floor1
"""
import time

from mininet.net import Containernet
from mininet.node import Controller
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import info, setLogLevel

import ipaddress
import os
import subprocess
import shlex

setLogLevel('info')

FLOORS = 0
SIM_FACTOR = 0.2
SIM_DURATION = 'inf'
CONTAINER_IMAGE = "antlabpolimi/fakey-sensors:attacks"
BROKER_IMAGE = "flipperthedog/mosquitto-cnet:latest"
path = os.getcwd()

# create list of ip addresses and remove 10.0.0.0
ip_list = [str(ip) for ip in ipaddress.IPv4Network('10.0.0.0/24')]
ip_list.pop(0)

room_devices = {
    "bulb": (2, "steady"),
    "camera": (1, "busy"),
    "fire": (1, "steady"),
    "plug": (5, "busy"),
    "smart_tv": (1, "busy"),
    "thermo": (1, "busy")
}

corridor_devices = {
    "bulb": (3, "busy"),
    "camera": (1, "busy"),
    "fire": (1, "steady"),
    "plug": (3, "steady"),
    "smart_tv": (0, "steady"),
    "thermo": (1, "steady")
}

spaces = {"room": room_devices,
          "corridor": corridor_devices}

floor_spaces = {"room": 0,
                "corridor": 0}

attackers = {"quick": 0,
             #"connect": 0,
             "heavy": 1}

attackers_ip = {"quick": "10.0.0.160",
             "connect": 0,
             "heavy": "10.0.0.162"}


class Floor:
    def __init__(self, floor_id):
        self.id = floor_id
        self.name = "f{}".format(self.id)
        self.rooms_number = 2
        self.switch = net.addSwitch(self.name)
        self.rooms = self.create_rooms()

    def get_switch(self):
        return self.switch

    def create_rooms(self):
        info('*** Creating rooms in floor {}\n'.format(self.name))
        floor_rooms = []
        for key, val in floor_spaces.items():
            floor_rooms = floor_rooms + [key] * val

        return [Room(ind, _type, self.name) for ind, _type in enumerate(floor_rooms)]

    def get_rooms(self):
        return self.rooms


class Room:
    def __init__(self, room_id, space_type, _floor):
        self.id = room_id
        self.floor = _floor
        self.name = "{}{}{}".format(self.floor, space_type[0], self.id)
        self.type = space_type
        self.devices = []

        self.switch = net.addSwitch('s{}{}'.format(self.id, self.name))
        self.create_space()

    def create_sensor(self, dev_type, sens_name, profile):
        return net.addDocker(sens_name, ip=ip_list.pop(0), dimage=CONTAINER_IMAGE,
                             environment={
                                 "SENS_BROKER": "10.0.0.251",
                                 "SENS_PORT": 1883,
                                 "DEVICE": dev_type,
                                 "SENS_NAME": sens_name,
                                 "SENS_ROOM": self.name,
                                 "SENS_FLOOR": "floor{}".format(self.floor),
                                 "SIM_FACTOR": SIM_FACTOR,
                                 "SIM_DURATION": SIM_DURATION,
                                 "T_PROFILE": profile}
                             )

    def get_switch(self):
        return self.switch

    def get_sensors(self):
        return self.devices

    def get_name(self, device, index):
        return "{}{}{}".format(self.name, device[0], index)

    def create_space(self):
        for device, info in spaces[self.type].items():
            for index in range(0, info[0]):
                dev = self.create_sensor(device, self.get_name(device, index), info[1])
                self.devices.append(dev)

        for _sensor in self.devices:
            net.addLink(self.switch, _sensor)

        return self.devices


info('*** Current directory {}\n'.format(path))

net = Containernet(controller=Controller)
info('*** Adding controller\n')
net.addController('c0')

# TODO: remove 251 from the ip addresses list
info('*** Adding docker broker using {}\n'.format(BROKER_IMAGE))
d1 = net.addDocker('d1', ip='10.0.0.251', dimage=BROKER_IMAGE,
                   ports=[1883], port_bindings={1883: 1883})

#info('*** Building the building\n\n')
#info('*** Creating floors...\n')
#floors = [Floor(indx) for indx in range(0, FLOORS)]

#for floor in floors:
    # link floor and rooms
#    for room in floor.get_rooms():
#        net.addLink(floor.get_switch(), room.get_switch(), cls=TCLink, delay='1ms', bw=1)

info('*** Creating attackzzz...\n')

attack_cont = list()
for attack, num in attackers.items():
    a = net.addDocker(attack, ip=attackers_ip[attack], dimage=CONTAINER_IMAGE,
                      environment={
                          "SENS_BROKER": "10.0.0.251",
                          "SENS_PORT": 1883,
                          "DEVICE": "attack",
                          "SENS_ROOM": "attack_room",
                          "SENS_FLOOR": "everywhere",
                          "SIM_FACTOR": SIM_FACTOR,
                          "SIM_DURATION": SIM_DURATION,
                          "ATTACK_NAME": attack}
                      )
    attack_cont.append(a)


info('*** Adding switches\n')
broker_switch = net.addSwitch('b1')
s_att = net.addSwitch('s666')

info('*** Creating links\n')
print(net.addLink(d1, broker_switch))

# switch - attacker link
for att in attack_cont:
    print(net.addLink(s_att, att, cls=TCLink, delay="1ms", bw=1))

# floor - broker links
#for floor in floors:
#    print(net.addLink(broker_switch, floor.get_switch()))

# broker - attacker link
info('\n', net.addLink(broker_switch, s_att))

info('*** Starting network\n')
net.start()
info('*** Testing connectivity\n')
net.pingAll()

info('*** Get switch interfaces\n')
net_interfaces = broker_switch.cmd("ls /sys/class/net/ | grep 'b1-'")
net_interfaces = \
    list(filter(None, net_interfaces.replace('\n', '').split('\r')))
print(net_interfaces)

info('*** Starting tcpdump\n')
tcp_pids = []
for eth in net_interfaces:
    cmd_tcpdump = "tcpdump -i {eth} -w {folder}/experiments/{eth}.pcap -q".format(eth=eth,
                                                                                  folder=os.path.expanduser(path))
    print(cmd_tcpdump)
    tcp_pids.append(subprocess.Popen(shlex.split(cmd_tcpdump), stderr=subprocess.DEVNULL))

print(tcp_pids)

info('*** Killing docker net interface\n')
d1.cmd("ip link set eth0 down")

# for floor in floors:
#     for room in floor.get_rooms():
#         for dev in room.get_sensors():
#             dev.cmd("ip link set eth0 down")

info('*** Starting the entrypoints\n')
d1.start()

time.sleep(5)
# for floor in floors:
#     for room in floor.get_rooms():
#         for dev in room.get_sensors():
#             dev.start()
#             time.sleep(1)

for att in attack_cont:
    att.start()

info('*** Running CLI\n')
CLI(net)

info('*** Stopping tcpdump\n')
for pid in tcp_pids:
    pid.terminate()

info('*** Stopping network\n')
net.stop()
