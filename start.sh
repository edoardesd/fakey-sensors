#!/bin/sh


echo Running the "$DEVICE".

python "${DEVICE}/${DEVICE}_user.py" &
python "${DEVICE}/${DEVICE}_device.py"