# MQTT Sensors Traffic Profiles
## Light Bulbs
### Traffic profiles
According to the type of room, we can identify two types of traffic profiles for any light bulb:
* **Busy Profile**: lights are turned on and off relatively often. This is compatible with closet rooms (whose light are for the time necessary to collect any item) and corridors (whole light turn on when people pass through, and then turn off automatically),
* **Steady profile**: once they are on, lights stay in this state for relatively longer intervals. This is compatible with living rooms, halls and any other space where people sojourn for longer periods of time

Here is a table of on/off transition rates for both profiles and peak hours:

| Profile    | On-off Rates    | Off-on Rates    |
| ---------- | --------------- | --------------- |
| **Busy**   | 30 changes/hour | 30 changes/hour |
| **Steady** | 5 changes/hour  | 30 changes/hour |

_Busy_ is symmetrical, meaning that the light will stay in both states for the same amount of time. _Steady_ tends to stay on for much longer than it stays off.

### Defining hourly rates

Independently of the traffic profiles mentioned above, we need transitions rates for the CT-MC that models the light bulb. Ideally lights are needed during dark hours, especially around evening and early morning. 

Considering the rates in the table above, we can decrease the off-on rates as we leave peak hours. This way, the light will turn on less often as intended, but the behaviour of the users will remain unchanged. 

Hourly hours are obtained summing two gaussian distributions: one centered at 5am and the other at 20pm and both with a variance of 2. Hourly off-on rates are then obtained according to the following formula:
$$
r(h) = 30\frac{f_1(h)+f_2(h)}{\max_{t}\{f_1(t)+f_2(t)\}}
$$
Note that this function is symmetrical around 12. 