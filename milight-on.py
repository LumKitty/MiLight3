#!/usr/bin/python
import sys,milightbox
milight = milightbox.MiLight3()
z = int(sys.argv[1])

temp = 0

if z > 0:
    milight.zone[z].fadetowhite(100, temp)
else:
    milight.ibox.fadeval(0,100)

milight.close()
