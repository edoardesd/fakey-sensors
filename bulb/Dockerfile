FROM python:3.10.0a5-alpine3.13

ENV WS_PORT 8080
ENV BROKER_PORT 1883
ENV DISTRIBUTED_FLAG true
ENV TOPOLOGY tree
ENV CLUSTER_SIZE 7
ENV BROKER_NUM 1
ENV LOCAL_FLAG false
ENV IP_ADDR 172.0.0.2

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    net-tools \
    iputils-ping \
    iproute2 \
    tcpdump \
    iperf \
    net-tools

WORKDIR /home/device/

RUN git clone https://github.com/edoardesd/fakey-sensors.git

RUN pip install fakey-sensors/requirements.txt

RUN chmod +x /home/device/fakey-sensors/bulb/start.sh

CMD ["/home/device/fakey-sensors/bulb/start.sh"]