#!/usr/bin/python
import sys,milightbox
milight = milightbox.MiLight3()
z = int(sys.argv[1])

if z > 0:
    milight.zone[z].fadeoff()
else:
    milight.ibox.fadeoff()

milight.close()