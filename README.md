# MiLight3
Python 2.7 control class for controlling MiLight-3.0 (Limitless V6.0) lights.  
Zone support should be working. Internal iBox light is not supported.
Also includes a handy module for detecting night/day so you can use the warm/cool white features in a manner similar to f.lux, twilight, redshift etc.

# Requirements:
Fasteners is required for lockfile support: https://pypi.python.org/pypi/fasteners
PyEphem is required for the isday.py and the supplied on/off scripts: http://rhodesmill.org/pyephem/

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
python "%USERPROFILE%\Downloads\get-pip.py"
pip install fasteners
pip install ephem
```

# Initial configuration
Edit isday.py and fill in your longitude, lattitude and elevation

# Advanced configuration
Settings in milightbox.py
```python
UDP_PORT_RECEIVE = 55054      # If for some reason another app uses this port you can change it
UDP_TIMES_TO_SEND_COMMAND = 2 # UDP is buggy. Increase this if you get ignored commands
SLEEP_TIME = 0.02             # (seconds) The delay between sending commands. Some lights, such as the
                              # downlights can't handle commands going too fast. If you only have bulbs
							  # you can use 0.01 to get faster smooth fades
DEFAULT_SPEED = 1             # For fade commands. Increments in steps of 1. Increase for faster fades,
                              # too high will cause a stuttering effect.
STATUSFILE = "./milight"      # Gets expanded to a filename such as "./milight-3-192.168.0.14.dat". 
STATUSEXT = ".dat"            # Raspberry Pi users may want to change this to "/tmp/milight/" to reduce 
                              # SD card usage, but this will cause weirdness the first time you use each 
							  # light after a reboot unless you write shutdown/startup scripts to 
							  # backup/restore this directory
DEBUG = 1                     # Set this to 0 to get rid of all the text spam!
IP = "192.168.0.14"           # Default IP address to use if not specified in your scripts. If you only
                              # have one milight box this can be a time saver!
```
Settings in isday.py
```python
LONGITUDE = 51.4   # Longitude. Use negative numbers for the southern hemisphere
LATTITUDE = -3.2   # Lattitude. Use negative numbers foe western hemisphere (Wales, USA, Spain etc.)
ELEVATION = 75     # Your height above sea level. Not a huge issue if you don't know it
HORIZON = -6       # How far below the horizon is considered sunset/rise. -6 is civil twilight
TEMPERATURE = 20   # Temperature to assume. Set it to an average sunset/sunrise temperature for your area
PRESSURE = 1019.5  # Atmospheric pressure. Probably want to leave this as the default
```
The elevation, temperature and pressure settings will all make sunrise/sunset detection more accurate, but most people are unlikely to need that level of accuracy. Basically the local air conditions cause the sun's light to be refracted possibly changing the time of your local sunset.
If you happen to have an outside weather station then the IsDay and IsNight functions can accept these parameters for increased accuracy, but the example scripts to not use this. Note that the advanced version is more accurate than that provided in Domoticz, so if you really want to use this you'll need to fire the script some time before sunset and wait until the correct time.

# Commandline usage with the example scripts
```
milight-on.py 1     # Turn zone 1 on - This will select warm white or cool white depending on time of day
milight-off.py 2    # Turn zone 2 off
milight-temp.py all # Gradually fade all white lights to warm or cool white as appropriate, over the course
                    # of one hour. Note that the all parameter is not supported in the on/off scripts yet
```

# Usage in Domoticz
Create virtual/dummy switches for each milight zone and call them as script on/off actions eg.
script:///home/pi/milight/milight-on.py 1
Create a scene set to trigget at both sunrise and sunset and have it call the temperature script eg.
script:///usr/bin/nohup /home/pi/milight/milight-temp.py all

# Usage in your own scripts:
```python
#!/usr/bin/python
import milightbox
milight = milightbox.MiLight3("192.168.1.1")                 # hostname/IP and port are optional

# Basic bulb colour setting commands

milight.zone[1].on(100)            # Turn zone 1 on at 100% brightness # brightness optional but recommended
milight.zone[2].off()              # Turn zone 2 off
milight.zone[3].night()            # Set zone 3 to nightlight   # this resets colour temperature to COOL
                                                                # as the nightlight is in cool white
milight.zone[4].white()            # Set zone 4 to white
milight.zone[1].brightness(50)     # Set zone 1 to 50% brightness      # works on both white and colour
milight.zone[1].colour(255,50,100) # Set zone 1 to hue 255, 50% saturation, 100% brightness
milight.zone[1].saturation(50)     # Set zone 1 to 50% saturation      # works on colour only
milight.zone[1].temperature(0)     # Set zone 1 to warm white          # works on white only
milight.zone[1].status()           # Print the current stored values for zone 1 - used for debugging
print milight.zone[1]._hue		   # Show the hue setting for zone 1 (-1 = white)
print milight.zone[1]._sat         # Show the saturation setting for zone 1. Undefined if white, -1 if off
print milight.zone[1]._val         # Show the brightness setting for zone 1. 0=NightLight, 1=0%, 101=100%
print milight.zone[1]._tmp         # Show the colour temperature for zone 1. 0=Warm, 100=Cold

# Fade commands - in all cases there is an optional speed parameter not shown. Note these only work correctly
#                 if you don't mess with the bulbs via an external method, such as the app or remote control
#                 These commands handle transition from night, colour or white to colour or white

milight.zone[1].fadetocolour(255,0,100) # Smoothly fade zone 1 to pure red at 100% brightness
milight.zone[1].fadetowhite(50,100)     # Smoothly fade zone 1 to cold white at 50% brightness
milight.zone[1].fadeoff()               # Smoothly fade out zone 1 then turn it off
milight.zone[1].fadetotemp(0)           # Smoothly fade zone 1 to warm white

milight.close()	                   # Write out the current values to the status file - must call this before
                                   # exitting as it's used for saving bulb state information
import isday
print isday.IsDay()           # True if the sun is still visible in the sky
print isday.IsNight()         # True if the sun has not set yet
print isday.IsDay(32, 900)    # More accurate IsDay() if the current temperature is 32C with an air
                              # pressure of 900
print isday.IsNight(-5, 1300) # More accurate IsNight using temp/pressure settings
print isday.IsDay_CustomPos(-27.1425519, 144.0248818, 100) # True if it's daytime in Brisbane, Australia
print isday.IsNight_CustomPos(-27.1425519, 144.0248818, 100, 50, 1019.5) # As above only the temp is 50C
next_sunset, next_sunrise = GetSunTimes() # Return a datetime containing next sunset and sunrise
next_sunset, next_sunrise = GetSunTimes(-27.1425519, 144.0248818, 100, 50, 1019.5) # Custom location/temp
```
# iBox light support ***BROKEN***
Same commands as above only in the form milight.ibox.off() 
Not all make sense (eg. saturation) and some don't even work as the documentation is wrong
Please don't consider iBox support ready for production use, in fact don't use it at all, seriously!

