import socket,sys,time,os,ephem;

# Some configuration settings
# iBox IP (and UDP port 5987)
IP = "192.168.0.14"
PORT = 5987
UDP_PORT_RECEIVE = 55054
UDP_TIMES_TO_SEND_COMMAND = 2
SLEEP_TIME = 0.02
DEFAULT_SPEED = 1
STATUSFILE = "/tmp/milight.dat"

LATTITUDE = -3.24
LONGITUDE = 51.41
ELEVATION = 0


class MiLight3:
    def __init__(self, ip=IP, port=PORT):
        MESSAGE = "20 00 00 00 16 02 62 3A D5 ED A3 01 AE 08 2D 46 61 41 A7 F6 DC AF D3 E6 00 00 1E"
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('', UDP_PORT_RECEIVE))
        sock.sendto(bytearray.fromhex(MESSAGE), (ip, port))
        sock.close()

        sockreceive = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sockreceive.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sockreceive.bind(('', UDP_PORT_RECEIVE))

        data, addr = sockreceive.recvfrom(65536)
        ##print "[DEBUG]received message:", data.encode('hex') 
        sockreceive.close()
        response = str(data.encode('hex'))
        iboxId1 = response[38:40]
        iboxId2 = response[40:42]
        ##print "[DEBUG]requesting iBox to execute command", iboxId1
        ##print "[DEBUG]requesting iBox to execute command", iboxId2

        self.header = "80 00 00 00 11 " + iboxId1 + " " + iboxId2 + " 00 SN 00 "
        self.seq = 0
        self.ip = ip
        self.port = port
        self._hue = [255,-1,-1,-1,-1]
        self._sat = [255, 0, 0, 0, 0]
        self._val = [255,-1,-1,-1,-1]
        self._tmp = [255, 0, 0, 0, 0]
        
	try:
            if os.path.isfile(STATUSFILE):
                statusfile = open(STATUSFILE,"r")
                for n in range(1,5):
                    self._hue[n] = int(statusfile.readline())
                    self._sat[n] = int(statusfile.readline())
                    self._val[n] = int(statusfile.readline())
                    self._tmp[n] = int(statusfile.readline())
                statusfile.close()
        except:
            print "Error reading saved milight data"

    def __del__(self):
        statusfile = open(STATUSFILE,"w")
        for n in range(1,5):
            statusfile.writelines(str(self._hue[n])+"\n")
            statusfile.writelines(str(self._sat[n])+"\n")
            statusfile.writelines(str(self._val[n])+"\n")
            statusfile.writelines(str(self._tmp[n])+"\n")
        statusfile.close()

    def rawsend(self, command):
        socksendto = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        socksendto.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        socksendto.bind(('', UDP_PORT_RECEIVE))
        for x in range(0, UDP_TIMES_TO_SEND_COMMAND):
            socksendto.sendto(bytearray.fromhex(command), (self.ip, self.port))
        socksendto.close()

    def send(self, command, zone):
        command = command + " " + format(zone, "02X")
        checksum = 0
        for n in bytearray.fromhex(command):
            checksum += n
        checksumhex = format(checksum, "04X")
        ##print "[DEBUG] Checksum:", checksumhex
        command = command + " 00 " + format(checksum, "04X")[2:]
        command = self.header.replace("SN", format(self.seq, "02X")) + command
        ##print "[DEBUG]sending message to the smart bulbs:", command
        self.rawsend(command)
        self.seq += 1
        if (self.seq >= 255):
            self.seq = 0
        ##print "[DEBUG]message(s) sent!"
        time.sleep(SLEEP_TIME)

    def rawon(self, zone):
        self.send("31 00 00 08 04 01 00 00 00", zone)

    def rawoff(self,zone):
        self.send("31 00 00 08 04 02 00 00 00", zone)

    def hue(self,zone,hue):
        if hue >=0 and hue <= 255:
            val = " " + format(hue, "02X")[:2]
            self.send("31 00 00 08 01"+val+val+val+val, zone)
            if self._hue[zone] == -1:
                self.val(zone,self._val[zone])
            self._hue[zone] = hue
        
    def sat(self,zone,sat):
        if sat >=0 and sat <= 100:
            val = format(sat, "02X")[:2]
            self.send("31 00 00 08 02 "+val+" 00 00 00", zone)
            self._sat[zone] = sat

    def val(self,zone,bri):
        if bri >=0 and bri <= 100:
            val = format(bri, "02X")[:2]
            self.send("31 00 00 08 03 "+val+" 00 00 00", zone)
            self._val[zone] = bri+1

    def temp(self,zone,temp):
        val = format(temp, "02X")[:2]
        self.send("31 00 00 08 05 "+val+" 00 00 00", zone)
        self._tmp[zone] = temp

    def hsv(self,zone,hue,sat,val):
        self.hue(zone,hue)
        self.sat(zone,sat)
        self.val(zone,val)

    # Basic Commands

    def on(self, zone, val=None):
        self.rawon(zone)
        if self._hue[zone] == -1:
            self.temp(zone,self._tmp[zone])
        else:
            self.hue(zone,self._hue[zone])
            self.sat(self._sat[zone])
        if val is None:
            if self._val[zone] == 0:
                self.val(zone,0)
            else:
                self.val(abs(self._val[zone])-1)
        else:
            self.val(zone,val)
        
    def off(self,zone):
        self.send("31 00 00 08 03 00 00 00 00", zone) # Set Brightness to zero before turn off
        self.rawoff(zone)
        self._val[zone] = -1
        
    def night(self,zone):
        self.send("31 00 00 08 04 05 00 00 00", zone)
        self._val[zone] = 0
        self._hue[zone] = -1
        self._tmp[zone] = 100

    def white(self,zone):
        self.rawon(zone)
        self.send("31 00 00 08 05 64 00 00 00", zone)
        if self._hue[zone] != -1:
            self.val(zone,self._val[zone]-1)
            self._hue[zone] = -1
            
    def brightness(self,zone,bri):
        self.rawon(zone)
        self.val(zone,bri)

    def saturation(self,zone,sat):
        self.rawon(zone)
        self.sat(zone,sat)
        
    def temperature(self,zone,temp):
        self.rawon(zone)
        self.temp(zone,temp)

    def colour(self,zone,hue,sat,val):
        self.rawon(zone)
        self.hsv(zone,hue,sat,val)

    def status(self,zone=None):
        if zone is None:
            zones = range(1,4)
        else:
            zones = [zone]
        for zone in zones:
            print "Zone       :",zone
            print "Hue        :",self._hue[zone]
            print "Saturation : "+str(self._sat[zone])+"%"
            print "Value      : "+str(self._val[zone]-1)+"%"
            print "Temperature: "+str(self._tmp[zone])+"%"
            print

    # Fancy Internal Commands

    def fadeval(self,zone,sourceval,destval,speed=DEFAULT_SPEED):
        if sourceval != destval:
            if sourceval < destval:
                speed = abs(speed)
            elif sourceval > destval:
                speed = -abs(speed)
        
            for n in range(sourceval,destval,speed):
                self.val(zone,n)
        self.val(zone,destval)

    def fadetemp(self,zone,sourcetemp,desttemp,speed=DEFAULT_SPEED):
        if sourcetemp != desttemp:
            if sourcetemp < desttemp:
                speed = abs(speed)
            elif sourcetemp > desttemp:
                speed = -abs(speed)
        
            for n in range(sourcetemp,desttemp,speed):
                self.temp(zone,n)
        self.temp(zone,desttemp)

    def fadewhite(self,zone,sourceval,destval,sourcetemp,desttemp,speed=DEFAULT_SPEED):
        valsteps  = abs(sourceval-destval)
        tempsteps = abs(sourcetemp-desttemp)
        if tempsteps > valsteps:
            steps = tempsteps / speed
        else:
            steps = valsteps / speed
        
        val=sourceval
        temp=sourcetemp

        if val > destval:
            valstep = -speed
        elif val < destval:
            valstep = speed
        else:
            valstep = 0

        if temp > desttemp:
            tempstep = -speed
        elif temp < desttemp:
            tempstep = speed
        else:
            tempstep = 0

        for n in range(0,steps):
            if valstep < 0:
                if val > destval:
                    val += valstep
                    if val < destval:
                        val = destval
            elif valstep > 0:
                if val < destval:
                    val += valstep
                    if val > destval:
                        val = destval

            if tempstep < 0:
                if temp > desttemp:
                    temp += tempstep
                    if temp < desttemp:
                        temp = desttemp
            elif tempstep > 0:
                if temp < desttemp:
                    temp += tempstep
                    if temp > desttemp:
                        temp = desttemp

            self.val(zone,val)
            self.temp(zone,temp)
           #print val,temp

        self.val(zone,destval)
        self.temp(zone,desttemp)


    def whitetohsv(self,zone,sourceval,desthue,destsat,destval, speed=DEFAULT_SPEED):
        valsteps = abs(sourceval-destval)
        satsteps = 100-destsat
        if satsteps > valsteps:
            steps = satsteps / speed
        else:
            steps = valsteps / speed
        sat=100
        val=sourceval
        if val > destval:
            valstep = -speed
        elif val < destval:
            valstep = speed
        else:
            valstep = 0
        self.hsv(zone,desthue,sat,sourceval)
        for n in range(0,steps):
            if sat > destsat:
                sat -= speed
                if sat < destsat:
                    sat = destsat
            if valstep < 0:
                if val > destval:
                    val += valstep
                    if val < destval:
                        val = destval
            elif valstep > 0:
                if val < destval:
                    val += valstep
                    if val > destval:
                        val = destval
            self.sat(zone,sat)
            self.val(zone,val)

    def hsvtowhite(self,zone,sourcehue,sourcesat,sourceval,destval,temp=None, speed=DEFAULT_SPEED):
        valsteps = abs(sourceval-destval)
        satsteps = 100-sourcesat
        if satsteps > valsteps:
            steps = satsteps / speed
        else:
            steps = valsteps / speed
        sat=sourcesat
        val=sourceval
        if val > destval:
            valstep = -speed
        elif val < destval:
            valstep = speed
        else:
            valstep = 0
        self.hsv(zone,sourcehue,sat,val)
        for n in range(0,steps):
            if sat < 100:
                sat += speed
                if sat > 100:
                    sat = 100
            if valstep < 0:
                if val > destval:
                    val += valstep
                    if val < destval:
                        val = destval
            elif valstep > 0:
                if val < destval:
                    val += valstep
                    if val > destval:
                        val = destval
            self.sat(zone,sat)
            self.val(zone,val)
        self.white(zone)
        self.val(zone,destval)
        if temp is not None:
            self.temp(temp)

    def hsvtohsv(self,zone,sourcehue,sourcesat,sourceval,desthue,destsat,destval,speed=DEFAULT_SPEED):
        valsteps = abs(sourceval-destval)
        satsteps = abs(sourcesat-destsat)
        huesteps = abs(sourcehue-desthue)

        hue=sourcehue
        sat=sourcesat
        val=sourceval

        if hue > desthue:
            huestep = -speed
        elif hue < desthue:
            huestep = speed
        else:
            huestep = 0       

        if huesteps > 127:
            huesteps = 256 - huesteps
            huestep = -huestep

       #print huestep
       #print huesteps

        if sat > destsat:
            satstep = -speed
        elif val < destval:
            satstep = speed
        else:
            satstep = 0

        if val > destval:
            valstep = -speed
        elif val < destval:
            valstep = speed
        else:
            valstep = 0

        if satsteps > valsteps:
            steps = satsteps
        else:
            steps = valsteps

        if huesteps > steps:
            steps = huesteps

        steps = steps / speed

        self.hsv(zone,hue,sat,val)
        for n in range(0,steps):

            if huestep < 0:
                hue += huestep
                if hue < 0:
                    hue += 256
                if abs(desthue-hue) < abs(speed):
                    hue = desthue
            elif huestep > 0:
                hue += huestep
                if hue > 255:
                    hue -= 256
                if abs(desthue-hue) < abs(speed):
                    hue = desthue
            
            if satstep < 0:
                if sat > destsat:
                    sat += satstep
                    if sat < destsat:
                        sat = destsat
            elif satstep > 0:
                if sat < destsat:
                    sat += satstep
                    if sat > destsat:
                        sat = destsat

            if valstep < 0:
                if val > destval:
                    val += valstep
                    if val < destval:
                        val = destval

            elif valstep > 0:
                if val < destval:
                    val += valstep
                    if val > destval:
                        val = destval
            self.hsv(zone,hue,sat,val)
           #print hue,sat,val

#   Fancy commands

    def fadetocolour(self,zone,hue,sat,val,speed=DEFAULT_SPEED):
        self.rawon(zone)
        if self._hue[zone] == -1:
            self.whitetohsv(zone,self._val[zone]-1,hue,sat,val,speed)
        else:
            self.hsvtohsv(zone,self._hue[zone],self._sat[zone],self._val[zone]-1,hue,sat,val,speed)

    def fadetowhite(self,zone,val,temp=None,speed=DEFAULT_SPEED):
        self.rawon(zone)        
        if self._hue[zone] == -1:
            if self._val[zone] == 0:
                self.rawon(zone)
                self.temp(zone,100)
            if temp is None:
                self.fadeval(zone,self._val[zone],val,speed)
            else:
                self.fadewhite(zone,self._val[zone]-1,val,self._tmp[zone],temp,speed)
        else:
            self.hsvtowhite(zone,self._hue[zone],self._sat[zone],self._val[zone]-1,val, temp, speed)

    def fadeoff(self,zone,speed=DEFAULT_SPEED):
        if self._val > 0:
            self.fadeval(zone,self._val[zone]+1,0,speed)
        self.off(zone)


    def fadetotemp(self,zone,temp,speed=DEFAULT_SPEED):
        if self._hue[zone] == -1 and self._val[zone] > 0:
            self.fadetemp(zone,self._tmp[zone],temp,speed)
        else:
            self.hsvtowhite(zone,self._hue[zone],self._sat[zone],self._val[zone]-1,val, temp, speed)

def IsDay(city=None):
    pos = ephem.Observer()
    pos.lat = str(LATTITUDE)
    pos.long = str(LONGITUDE)
    pos.elevation = ELEVATION

    #pos.temp = 20            # current air temperature gathered manually
    #pos.pressure = 1019.5    # current air pressure gathered manually

    next_sunrise = pos.next_rising( ephem.Sun()).datetime()
    next_sunset = pos.next_setting(ephem.Sun()).datetime()

    result = next_sunset < next_sunrise

    return result
