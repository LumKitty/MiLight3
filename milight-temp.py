#!/usr/bin/python
import sys,time,milightbox,isday

SPEED = 1
DELAY = 35
# To run over the course of one hour do
# DELAY = 60(seconds) * 60(minutes) / 101(number of fade steps)

if sys.argv[1] == "all":
	zones = range(1,5)
else:
	zones = [int(sys.argv[1])]

if isday.IsDay():
	targettemp = 100
else:
	targettemp = 0

print "Setting temperature to",targettemp


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
