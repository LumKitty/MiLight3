#!/usr/bin/python
import sys,milightbox,isday
milight = milightbox.MiLight3()
z = int(sys.argv[1])

if isday.IsDay():
    temp = 100
else:
    temp = 0

if z > 0:
    milight.zone[z].fadetowhite(100, temp)
else:
    milight.ibox.fadeval(0,100)

milight.close()
