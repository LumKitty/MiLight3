#!/usr/bin/python
import sys,milightbox
milight = milightbox.MiLight3()
if sys.argv[1] == "all":
	zones = range(1,5)
else:
	zones = [int(sys.argv[1])]

if milightbox.IsDay():
	temp = 100
else:
	temp = 0

for n in zones:
	if milight._hue[n] == -1 and milight._val[n] > 0:
		milight.fadetotemp(zone, 100, temp)
