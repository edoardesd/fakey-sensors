FROM python:3.8-alpine3.12

ENV DEVICE=thermo

ENV SENS_BROKER=172.17.0.3
ENV SENS_PORT=1883
ENV SENS_NAME="none0"
ENV SENS_ROOM="none0"
ENV SENS_FLOOR="none0"
ENV SIM_FACTOR=0.1
# for infinite duration use 'inf'
ENV SIM_DURATION='inf'
ENV T_PROFILE="busy"


RUN apk --no-cache --update-cache add git \
    iputils \
    iproute2 \
    net-tools \
    iperf \
    xterm \
    busybox-extras \
    bash


WORKDIR /home/device/fakey-sensors


COPY . .
#RUN git clone "https://github.com/edoardesd/fakey-sensors.git"
RUN pip install --no-cache-dir -r requirements.txt

RUN chmod +x start.sh

CMD ["./start.sh"]