# Make sure to install ephem before using this (pip install ephem)
# Windows users will need to install PIP first, instructions here:
# https://pip.pypa.io/en/stable/installing/#do-i-need-to-install-pip
# Both Windows and Linux users will then need to install epham:
# pip install ephem
import ephem, datetime, time
from milightbox import debugprint

# Set these to wherever you live. You can grab the numbers from a Google Maps
# search for your own address. They're hidden in the resulting URL.
LATTITUDE   = 51.4167
LONGITUDE   = -3.2467
ELEVATION   = 75

HORIZON     = -6 # -6  for civil twilight 
                 # -12 for nautical twilight
                 # -18 for astronomical twilight

# Set these to sensible defaults for wherever you live.
TEMPERATURE = 10
PRESSURE    = 1019.5

def GetSunTimes_CustomPos(lattitude=LATTITUDE,longitude=LONGITUDE,elevation=ELEVATION,horizon=HORIZON,temperature=TEMPERATURE,pressure=PRESSURE):
    pos = ephem.Observer()
    pos.long = str(longitude)
    pos.lat = str(lattitude)
    pos.elevation = elevation
    pos.temp = temperature
    pos.pressure = pressure
    pos.horizon = str(horizon)
    next_sunrise = pos.next_rising(ephem.Sun()).datetime()
    next_sunset = pos.next_setting(ephem.Sun()).datetime()
    return (next_sunrise, next_sunset)

def GetSunTimes(horizon=HORIZON,temperature=TEMPERATURE,pressure=PRESSURE):
    return GetSunTimes_CustomPos(LATTITUDE,LONGITUDE,ELEVATION,horizon,temperature,pressure)

# Use this variant if you need to override the location for some reason
def IsDay_CustomPos(lattitude,longitude,elevation,horizon=HORIZON,temperature=TEMPERATURE,pressure=PRESSURE):
    next_sunrise, next_sunset = GetSunTimes_CustomPos(lattitude,longitude,elevation,horizon,temperature,pressure)
    result = next_sunset < next_sunrise
    return result

# Normal people will use this variant. If you have temperature and pressure
# sensors then feel free to pass on their values for more accurate results
def IsDay(horizon=HORIZON,temperature=TEMPERATURE,pressure=PRESSURE):
    return IsDay_CustomPos(LATTITUDE, LONGITUDE, ELEVATION, horizon, temperature, pressure)

# Night time variants for the truly lazy
def IsNight_CustomPos(lattitude,longitude,elevation,horizon=HORIZON,temperature=TEMPERATURE,pressure=PRESSURE):
    return not IsDay_CustomPos(lattitude,longitude,elevation,horizon,temperature,pressure)

def IsNight(horizon=HORIZON,temperature=TEMPERATURE,pressure=PRESSURE):
    return not IsDay_CustomPos(LATTITUDE, LONGITUDE, ELEVATION, horizon, temperature, pressure)

def WaitUntilSunset_CustomPos(lattitude,longitude,elevation,horizon=HORIZON,temperature=TEMPERATURE,pressure=PRESSURE):
    next_sunrise, next_sunset = GetSunTimes_CustomPos(lattitude,longitude,elevation,horizon,temperature,pressure)
    timedelay = (next_sunset - datetime.datetime.utcnow()).total_seconds()
    debugprint("Current time      : "+str(datetime.datetime.utcnow())+" UTC")
    debugprint("Next sunset is at : "+str(next_sunset)+" UTC")
    debugprint("Next sunrise is at: "+str(next_sunrise)+" UTC")
    debugprint("Waiting for       : "+str(timedelay)+" seconds")
    time.sleep (timedelay)

def WaitUntilSunset(horizon=HORIZON,temperature=TEMPERATURE,pressure=PRESSURE):
    WaitUntilSunset_CustomPos(LATTITUDE, LONGITUDE, ELEVATION, horizon, temperature, pressure)

def WaitUntilSunrise_CustomPos(lattitude,longitude,elevation,horizon=HORIZON,temperature=TEMPERATURE,pressure=PRESSURE):
    next_sunrise, next_sunset = GetSunTimes_CustomPos(lattitude,longitude,elevation,horizon,temperature,pressure)
    timedelay = (next_sunrise - datetime.datetime.utcnow()).total_seconds()
    debugprint("Current time      : "+str(datetime.datetime.utcnow())+" UTC")
    debugprint("Next sunset is at : "+str(next_sunset)+" UTC")
    debugprint("Next sunrise is at: "+str(next_sunrise)+" UTC")
    debugprint("Waiting for       : "+str(timedelay)+" seconds")
    time.sleep (timedelay)

def WaitUntilSunrise(horizon=HORIZON,temperature=TEMPERATURE,pressure=PRESSURE):
    WaitUntilSunrise_CustomPos(LATTITUDE, LONGITUDE, ELEVATION, horizon, temperature, pressure)