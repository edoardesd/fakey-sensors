# Thermostat sensor

## Passive behaviour
The sensor reports on these values in 15 minutes intervals:
* ``desired_temp`` this is the temperature that is set as desired by the user  
* ``current_temp`` this is the measured temperature
* ``humidity`` even though humidity is somehow correlated with temperature, we just publish values from a triangular distribution
between 30 and 70 with mode 50.
  
  
## Active behaviour
The user will set a desired temperature for each hour of the day. Currently, we use the following:
* 20° from 0AM to 7AM
  
* 22° from 7AM to 10AM 
  
* 21° from 10AM to 23PM

* 20° from 23PM to 7AM

## Temperature variation simulation
At each status report interval, before publishing the status ``current_temp`` is updated according to the following formula:

``current_temp = current_temp + sign(desired_temp - current_temp)*max{abs(desired_temp - current_temp), 0.5}``

Then the measured temperature is further perturbed by adding a random value taken from a normal distribution with mean 0 
and variance 0.3