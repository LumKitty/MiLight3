# MiLight3
Python 2.7 control class for controlling MiLight-3.0 (Limitless V6.0) lights.  
Edit default settings in milightbox.py for IP, PORT speed etc.
I'll get around to it as I'm going to use it as a visual doorbell at some point.

# Usage:
```python
import milightbox
milight = milightbox.MiLight3("192.168.1.1")                 # hostname/IP and port are optional

# Basic bulb colour setting commands

milight.zone[1].on(100)            # Turn zone 1 on at 100% brightness # brightness optional but recommended
milight.zone[1].off()              # Turn zone 1 off
milight.zone[1].night()            # Set zone 1 to nightlight          # this resets colour temperature to COOL
                                                                       # nightlight is in cool white
milight.zone[1].white()            # Set zone 1 to white
milight.zone[1].brightness(50)     # Set zone 1 to 50% brightness      # works on both white and colour
milight.zone[1].colour(255,50,100) # Set zone 1 to hue 255, 50% saturation, 100% brightness
milight.zone[1].saturation(50)     # Set zone 1 to 50% saturation      # works on colour only
milight.zone[1].temperature(0)     # Set zone 1 to warm white          # works on white only
milight.zone[1].status()           # Print the current stored values for zone 1 - used for debugging

# Fade commands - in all cases there is an optional speed parameter not shown. Note these only work correctly if 
#                 you don't mess with the bulbs via an external method, such as the app or remote control.
#                 These commands handle transition from night, colour or white to colour or white

milight.zone[1].fadetocolour(255,0,100) # Smoothly fade zone 1 to pure red at 100% brightness
milight.zone[1].fadetowhite(50,100)     # Smoothly fade zone 1 to cold white at 50% brightness
milight.zone[1].fadeoff()               # Smoothly fade out zone 1 then turn it off
milight.zone[1].fadetotemp(0)           # Smoothly fade zone 1 to warm white

# iBox light support
# Same commands as above only in the form milight.ibox.off() 
# Not all make sense (eg. saturation) and some don't even work as the documentation is wrong
# Please don't consider iBox support ready for production use!
```
