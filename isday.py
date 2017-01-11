# Make sure to install ephem before using this (pip install ephem)
# Windows users will need to install PIP first, instructions here:
# https://pip.pypa.io/en/stable/installing/#do-i-need-to-install-pip
# Both Windows and Linux users will then need to install epham:
# pip install ephem
import ephem

# Set these to wherever you live. You can grab the numbers from a Google Maps
# search for your own address. They're hidden in the resulting URL.
LONGITUDE   = 51.4
LATTITUDE   = -3.2
ELEVATION   = 75

# Set these to sensible defaults for wherever you live.
TEMPERATURE = 20
PRESSURE    = 1019.5

def GetSunTimes(lattitude,longitude,elevation,temperature,pressure):
    pos = ephem.Observer()
    pos.long = str(longitude)
    pos.lat = str(lattitude)
    pos.elevation = elevation
    pos.temp = temperature
    pos.pressure = pressure
    next_sunrise = pos.next_rising(ephem.Sun()).datetime()
    next_sunset = pos.next_setting(ephem.Sun()).datetime()
    return (next_sunrise, next_sunset)

# Use this variant if you need to override the location for some reason
def IsDay_CustomPos(lattitude,longitude,elevation,temperature=TEMPERATURE,pressure=PRESSURE):
    next_sunrise, next_sunset = GetSunTimes(lattitude,longitude,elevation,temperature,pressure)
    result = next_sunset < next_sunrise
    return result

# Normal people will use this variant. If you have temperature and pressure
# sensors then feel free to pass on their values for more accurate results
def IsDay(temperature=TEMPERATURE,pressure=PRESSURE):
    return IsDay_CustomPos(LONGITUDE, LATTITUDE, ELEVATION, temperature, pressure)

# Night time variants for the truly lazy
def IsNight_CustomPos(lattitude,longitude,elevation,temperature=TEMPERATURE,pressure=PRESSURE):
    return not IsDay_CustomPos(lattitude,longitude,elevation,temperature,pressure)

def IsNight(temperature=TEMPERATURE,pressure=PRESSURE):
    return not IsDay_CustomPos(LONGITUDE, LATTITUDE, ELEVATION, temperature, pressure)