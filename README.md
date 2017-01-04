# MiLight3
Python 2.7 control class for controlling MiLight-3.0 (Limitless V6.0) lights.  
Edit default settings in milightbox.py  
Requires PyEphem for the IsDay function `pip install ephem` or just remove that whole function if you don't want it.

# Usage:
```python
import milightbox
milight = milightbox.MiLight3("192.168.1.1", 5987)           # hostname/IP and port are optional

# Basic bulb colour setting commands

milight.on(1,100)        # Turn zone 1 on at 100% brightness # brightness optional but recommended
milight.off(1)           # Turn zone 1 off
milight.night(1)         # Set zone 1 to nightlight          # this resets colour temperature to 100 (cool) as the
                                                             # nightlight is in cool white
milight.white(1)         # Set zone 1 to white
milight.brightness(1,50) # Set zone 1 to 50% brightness      # works on both white and colour
milight.colour(1,255,50,100) # Set zone 1 to hue 255, 50% saturation, 100% brightness
milight.saturation(1,50) # Set zone 1 to 50% saturation      # works on colour only
milight.temperature(1,0) # Set zone 1 to warm white          # works on white only
milight.status(1)        # Print the current stored values for zone 1 - used for debugging

# Fade commands - in all cases there is an optional speed parameter not shown. Note these only work correctly if 
#                 you don't mess with the bulbs via an external method, such as the app or remote control.
#                 These commands handle transition from night, colour or white to colour or white

milight.fadetocolour(1,255,0,100) # Smoothly fade zone 1 to pure red at 100% brightness
milight.fadetowhite(1,50,100)     # Smoothly fade zone 1 to cold white at 50% brightness
milight.fadeoff(1)                # Smoothly fade out zone 1 then turn it off
milight.fadetotemp(1,0)           # Smoothly fade zone 1 to warm white

print milight.IsDay()             # True if the sun hasn't set yet
```
