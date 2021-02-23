#!/bin/sh

device=$1

docker build --no-cache --tag antlabpolimi/fakey-sensors:"${device}" .
docker push antlabpolimi/fakey-sensors:"${device}"
