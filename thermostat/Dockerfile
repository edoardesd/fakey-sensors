FROM python:3.8-alpine3.12

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

# for numpy
RUN echo "http://dl-8.alpinelinux.org/alpine/edge/community" >> /etc/apk/repositories
RUN apk --no-cache --update-cache add gcc gfortran build-base wget freetype-dev libpng-dev openblas-dev
RUN ln -s /usr/include/locale.h /usr/include/xlocale.h

WORKDIR /home/device/

RUN git clone "https://github.com/edoardesd/fakey-sensors.git"
RUN pip install --no-cache-dir -r fakey-sensors/requirements.txt

WORKDIR /home/device/fakey-sensors/thermostat

RUN chmod +x start.sh

CMD ["./start.sh"]