#!/usr/bin/python
import sys,milightbox
milight = milightbox.MiLight3()
zone = int(sys.argv[1])

milight.fadeval(zone,milight._val[zone],0)
milight.off(zone)
