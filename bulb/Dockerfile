FROM python:3.10.0a5-alpine3.13

ENV WS_PORT 8080
ENV BROKER_PORT 1883
ENV DISTRIBUTED_FLAG true
ENV TOPOLOGY tree
ENV CLUSTER_SIZE 7
ENV BROKER_NUM 1
ENV LOCAL_FLAG false
ENV IP_ADDR 172.0.0.2

RUN apk add git \
    iputils \
    iproute2 \
    net-tools \
    iperf \
    xterm \
    busybox-extras

WORKDIR /home/device/

RUN git clone "https://github.com/edoardesd/fakey-sensors.git"

RUN pip install -r fakey-sensors/requirements.txt

RUN chmod +x /home/device/fakey-sensors/bulb/start.sh

CMD ["/home/device/fakey-sensors/bulb/start.sh"]