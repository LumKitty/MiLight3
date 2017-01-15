#!/usr/bin/python
import sys,time,datetime,milightbox,isday
from milightbox import debugprint

SPEED = 1
DELAY = 35
# To run over the course of one hour do
# DELAY = 60(seconds) * 60(minutes) / 101(number of fade steps)

if sys.argv[1] == "all":
	zones = range(1,5)
elif sys.argv[1] == "wait":
    zones = []
else:
	zones = [int(sys.argv[1])]

if (datetime.datetime.now().hour >12 and isday.IsDay(-6)) or isday.IsDay(0):
    targettemp = 0
    debugprint("Detected daytime. Waiting for sunset")
    if isday.IsDay(0):
        isday.WaitUntilSunset(0)
    next_sunrise,next_sunset=isday.GetSunTimes(-6)
    end_time = next_sunset
else:
    targettemp = 100
    debugprint("Detected nighttime. Waiting for sunrise")
    if isday.IsNight(-6):
        isday.WaitUntilSunrise(-6)
    next_sunrise,next_sunset=isday.GetSunTimes(0)
    end_time = next_sunrise

debugprint("Civil twilight time           : "+str(end_time))

delay = (end_time - datetime.datetime.utcnow()).total_seconds()
DELAY = delay * SPEED / 101

debugprint("Setting temperature to        : "+str(targettemp))
debugprint("Seconds between real and civil: "+str(delay))
debugprint("Delay between steps           : "+str(DELAY))


while True:
    finished = 0
    milight = milightbox.MiLight3()
    for n in zones:
        if milight.zone[n]._hue == -1 and milight.zone[n]._val > 0:
            if milight.zone[n]._tmp < targettemp:
                milight.zone[n].fadetotemp(milight.zone[n]._tmp+SPEED)
            elif milight.zone[n]._tmp > targettemp:
                milight.zone[n].fadetotemp(milight.zone[n]._tmp-SPEED)
            else:
                finished += 1
        else:
            finished += 1
    milight.close()
    if finished >= len(zones):
        break
    time.sleep(DELAY)

sys.exit(targettemp)
