# Fire sensor
The fire sensor has two working modes:
1. If no fire is detected, the sensor publishes a status report each 5 minutes on topic `status_update`
2. If a fire is detected, an alarm is sent by publishing the status on topic `fire_alarm`. Furthermore, the alarm is repeated each 30 seconds until the sensor keeps detecting fire, i.e. after exactly 5 minutes.
After this interval, the fire is considered extinguished, status is reported on topic `fire_alarm` and the sensor is back to working mode 1.
   
There is a 0.001 probability that a fire (or smoke) is detected at each status report, such that the probability of __not__
having a fire during a 24H period is around 0.75.

This sensor has no user interaction.
