"""
Example topology with two containers (d1, d2),
two switches, and one controller:

          - (c)-
            |
(broker) - (s1) - (device_0)
         - s2 - device_floor1
"""
from mininet.net import Containernet
from mininet.node import Controller
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import info, setLogLevel

import ipaddress

setLogLevel('info')

BULB_ROOM = 3
PLUGS_ROOM = 5
SIM_FACTOR = 0.2
SIM_DURATION = 'inf'
CONTAINER_IMAGE = "antlabpolimi/fakey-sensors:latest"
BROKER_IMAGE = "flipperthedog/mosquitto-cnet:latest"

# create list of ip addresses and remove 10.0.0.0
ip_list = [str(ip) for ip in ipaddress.IPv4Network('10.0.0.0/24')]
ip_list.pop(0)

room_devices = {
    "bulb": (2, "steady"),
    "camera": (1, "steady"),
    "fire": (0, "steady"),
    "plug": (1, "busy"),
    "smart_tv": (0, "steady"),
    "thermo": (0, "busy")
}

corridor_devices = {
    "bulb": (5, "busy"),
    "camera": (1, "steady"),
    "fire": (1, "steady"),
    "plug": (7, "steady"),
    "smart_tv": (0, "steady"),
    "thermo": (1, "steady")
}

spaces = {"room": room_devices,
          "corridor": corridor_devices}


def create_space(_type, num):
    _room_devices = []
    room_name = "room{}".format(num)

    for device, info in spaces[_type].items():
        for index in range(0, info[0]):
            sensor_name = "r{}{}{}".format(num, device[0], index)
            cont = net.addDocker(sensor_name, ip=ip_list.pop(0), dimage=CONTAINER_IMAGE,
                                 environment={
                                     "SENS_BROKER": "10.0.0.251",
                                     "SENS_PORT": 1883,
                                     "DEVICE": device,
                                     "SENS_NAME": sensor_name,
                                     "SENS_ROOM": room_name,
                                     "SENS_FLOOR": "floor0",
                                     "SIM_FACTOR": SIM_FACTOR,
                                     "SIM_DURATION": SIM_DURATION,
                                     "T_PROFILE": info[1]}
                                 )
            _room_devices.append(cont)

    return _room_devices


net = Containernet(controller=Controller)
info('*** Adding controller\n')
net.addController('c0')

# TODO: remove 251 from the ip addresses list
info('*** Adding docker broker using {}\n'.format(BROKER_IMAGE))
d1 = net.addDocker('d1', ip='10.0.0.251', dimage=BROKER_IMAGE,
                   ports=[1883], port_bindings={1883: 1883})

info('*** Adding rooms\n')
room_devices = []
switches = []


# create floor
floor_switch = net.addSwitch('floor{}'.format(0))

for _spaces in range(0, 2):
    s = net.addSwitch('s{}'.format(_spaces))
    switches.append(s)
    this_room = create_space("room", _spaces)

    for _sensor in this_room:
        print(_sensor)
        print(net.addLink(s, _sensor))

    room_devices = room_devices + this_room

print("\nSWITCHES: ", switches)
print("\n\nROOM\n", room_devices)

info('*** Adding switches\n')
s1 = net.addSwitch('b1')


info('*** Creating links\n')
net.addLink(d1, s1)
net.addLink(s1, floor_switch)

for s in switches:
     net.addLink(floor_switch, s, cls=TCLink, delay='1ms', bw=1)


info('*** Starting network\n')
net.start()
info('*** Testing connectivity\n')
net.pingAll()
info('*** Starting the entrypoints\n')
d1.start()
for dev in room_devices:
    dev.start()
info('*** Killing docker net interface\n')
d1.cmd("ip link set eth0 down")
for dev in room_devices:
    dev.cmd("ip link set eth0 down")
info('*** Running CLI\n')
CLI(net)
info('*** Stopping network')
net.stop()
