#!/bin/sh

echo Running the "$DEVICE".

if [ "$DEVICE" = "attack" ]; then
   echo "Achtung, running an attack!"
   python "${DEVICE}/start_stop.py"
else
  python "${DEVICE}/${DEVICE}_user.py" &
  python "${DEVICE}/${DEVICE}_device.py"
fi
