# MiLight3
Python 2.7 control class for controlling MiLight-3.0 (Limitless V6.0) lights.  
Zone support should be working. Internal iBox light support is still very broken.
Also includes a handy module for detecting night/day so you can use the warm/cool white features in a manner similar to f.lux, twilight, redshift etc.

# Requirements:
Fasteners is required for lockfile support: https://pypi.python.org/pypi/fasteners
PyEphem is required for the supplied on/off scripts: http://rhodesmill.org/pyephem/

# Preparation - Linux:
```
# sudo apt-get install pip
# pip install fasteners
# pip install ephem
```

# Preparation - Windows:
Download: https://bootstrap.pypa.io/get-pip.py
Open an admin command prompt and run
```
python get-pip.py
pip install fasteners
pip install ephem
```

# Initial configuration
Edit isday.py and fill in your longitude, lattitude and elevation
(optional) Edit milightbox.py and fill in your IP address)
# Commandline usage with the example scripts
```
milight-on.py 1     # Turn zone 1 on - This will select warm white or cool white depending on time of day
milight-off.py 2    # Turn zone 2 off
milight-temp.py all # Gradually fade all white lights to warm or cool white as appropriate, over the course of
                    # one hour. Note that the all parameter is not supported in the on/off scripts yet
```

# Usage in Domoticz
Create virtual/dummy switches for each milight zone and call them as script on/off actions eg.
script:///home/pi/milight/milight-on.py 1
Create a scene set to trigget at both sunrise and sunset and have it call the temperature script eg.
script:///home/pi/milight/milight-temp.py all

# Usage in your own scripts:
```python
#!/usr/bin/python
import milightbox
milight = milightbox.MiLight3("192.168.1.1")                 # hostname/IP and port are optional

# Basic bulb colour setting commands

milight.zone[1].on(100)            # Turn zone 1 on at 100% brightness # brightness optional but recommended
milight.zone[2].off()              # Turn zone 2 off
milight.zone[3].night()            # Set zone 3 to nightlight          # this resets colour temperature to COOL
                                                                       # nightlight is in cool white
milight.zone[4].white()            # Set zone 4 to white
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

milight.close()	                   # Write out the current values to the status file - must call this before
                                   # exitting as it's used for saving bulb state information
```
# iBox light support
Same commands as above only in the form milight.ibox.off() 
Not all make sense (eg. saturation) and some don't even work as the documentation is wrong
Please don't consider iBox support ready for production use, in fact don't use it at all!

