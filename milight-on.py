#!/usr/bin/python
import sys,milightbox
milight = milightbox.MiLight3()
zone = int(sys.argv[1])
if milightbox.IsDay():
	temp = 100
else:
	temp = 0
milight.fadetowhite(zone, 100, temp)
