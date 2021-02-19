#!/bin/sh

device=$1

docker build --no-cache --tag antlabpolimi/fakey-sensors:"${device}" .