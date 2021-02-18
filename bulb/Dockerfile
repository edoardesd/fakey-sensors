FROM python:3.10.0a5-alpine3.13

ENV SENS_BROKER=172.17.0.3
ENV SENS_PORT=1883
ENV SENS_NAME="none0"
ENV SENS_ROOM="none0"
ENV SENS_FLOOR="none0"
ENV SIM_FACTOR=0.1
# for infinite duration use 'inf'
ENV SIM_DURATION='inf'
ENV T_PROFILE="busy"

RUN apk add git \
    iputils \
    iproute2 \
    net-tools \
    iperf \
    xterm \
    busybox-extras \
    bash

#RUN git clone "https://github.com/edoardesd/fakey-sensors.git"

COPY . /home/device/fakey-sensors/

WORKDIR /home/device/fakey-sensors

RUN pip install -r requirements.txt

RUN chmod +x start.sh

CMD ["./start.sh"]