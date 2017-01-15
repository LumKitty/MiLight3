# Make sure to install fasteners before using this (pip install ephem)
# Windows users will need to install PIP first, instructions here:
# https://pip.pypa.io/en/stable/installing/#do-i-need-to-install-pip
# Both Windows and Linux users will then need to install epham:
# pip install fasteners
import socket,sys,time,os,fasteners;

# Some configuration settings
# iBox IP (and UDP port 5987)
UDP_PORT_RECEIVE = 55054
UDP_TIMES_TO_SEND_COMMAND = 3
IP            = "192.168.0.14"
SLEEP_TIME    = 0.05
DEFAULT_SPEED = 1
STATUSFILE    = "./milight"
STATUSEXT     = ".dat"
DEBUG = 1

def debugprint(message):
    if DEBUG == 1:
        print message

def debugprintnolf(message):
    if DEBUG == 1:
        print message,

class MiLight3:
    def __init__(self, ip=IP, port=5987):
        self.ip = ip        
        self.statusfilename = STATUSFILE+"3-"+self.ip+STATUSEXT
        debugprint("Status file: "+self.statusfilename)
        self.lock = fasteners.InterProcessLock(self.statusfilename+".lock")
        got = self.lock.acquire(True, 1, 1, 10)
        if not got:
            debugprint("Could not acquire lock")
            raise Exception("LockError")

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
        debugprint("received message: "+data.encode('hex'))
        sockreceive.close()
        response = str(data.encode('hex'))
        iboxId1 = response[38:40]
        iboxId2 = response[40:42]
        debugprint("requesting iBox to execute command "+iboxId1)
        debugprint("requesting iBox to execute command "+iboxId2)

        self.header = "80 00 00 00 11 " + iboxId1 + " " + iboxId2 + " 00 SN 00 "
        self.seq = 0
        self.ip = ip
        self.port = port
        self.zone = [0]
        if os.path.isfile(self.statusfilename):
            statusfile = open(self.statusfilename,"r")
            for n in range(1,5):
                try:
                    if statusfile.readline().strip() == "# Zone "+str(n):
                        hue = int(statusfile.readline().strip())
                        sat = int(statusfile.readline().strip())
                        val = int(statusfile.readline().strip())
                        tmp = int(statusfile.readline().strip())

                        debugprint("Statusfile zone "+str(n)+" valid - using stored values")
                        self.zone.append(rgbww(self,n,hue,sat,val,tmp))
                    else:
                        debugprint("Statusfile zone "+str(n)+" invalid - using defaults")
                        self.zone.append(rgbww(self,n))
                except Exception as ex:
                    debugprint("Error reading zone "+str(n)+" - using defaults")
                    debugprint(str(ex))
                    self.zone.append(rgbww(self,n))
            try:
                if statusfile.readline().strip() == "# iBox Light":
                    hue = int(statusfile.readline().strip())
                    val = int(statusfile.readline().strip())
                    debugprint("Statusfile iBox valid - using stored values")
                    self.ibox = iboxlight(self,hue,val)
                else:
                    debugprint("Statusfixe iBox invalid - using defaults")
                    self.ibox = iboxlight(self)
            except Exception as ex:
                debugprint("Error reading iBox - using defaults")
                debugprint(str(ex))
                self.ibox = iboxlight(self)

            statusfile.close()
        else:
            debugprint("No statusfile - using defaults")
            for n in range(1,5):
                self.zone.append(rgbww(self,n))
            self.ibox=iboxlight(self)

    def close(self):
        debugprint("Writing: "+self.statusfilename)
        statusfile = open(self.statusfilename,"w")
        for n in range(1,5):
            statusfile.writelines("# Zone "+str(n)+"\n")
            statusfile.writelines(str(self.zone[n]._hue)+"\n")
            statusfile.writelines(str(self.zone[n]._sat)+"\n")
            statusfile.writelines(str(self.zone[n]._val)+"\n")
            statusfile.writelines(str(self.zone[n]._tmp)+"\n")
        statusfile.writelines("# iBox Light\n")
        statusfile.writelines(str(self.ibox._hue)+"\n")
        statusfile.writelines(str(self.ibox._val)+"\n")
        statusfile.close()
        self.lock.release()

    def rawsend(self, command):
        socksendto = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        socksendto.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        socksendto.bind(('', UDP_PORT_RECEIVE))
        for x in range(0, UDP_TIMES_TO_SEND_COMMAND):
            socksendto.sendto(bytearray.fromhex(command), (self.ip, self.port))
        socksendto.close()
        debugprint("Sent to IP: "+self.ip)

class milight3light:    # Commands common to rgbww and iboxlight
    def send(self, command):
        command = command + " " + format(self.zone, "02X")
        checksum = 0
        for n in bytearray.fromhex(command):
            checksum += n
        checksumhex = format(checksum, "04X")
        command = command + " 00 " + format(checksum, "04X")[2:]
        command = self.parent.header.replace("SN", format(self.parent.seq, "02X")) + command
        debugprintnolf(str(self.zone)+" sending message: "+ command)
        self.parent.rawsend(command)
        self.parent.seq += 1
        if (self.parent.seq >= 255):
            self.parent.seq = 0
        time.sleep(SLEEP_TIME)
   
    def fadeval(self,sourceval,destval,speed=DEFAULT_SPEED):
        if sourceval != destval:
            if sourceval < destval:
                speed = abs(speed)
            elif sourceval > destval:
                speed = -abs(speed)
        
            for n in range(sourceval,destval,speed):
                self.val(n)
        self.val(destval)
   
    def fadeoff(self,speed=DEFAULT_SPEED):
        if self._val > 0:
            self.fadeval(self._val-1,0,speed)
        self.off()

    def hue(self,hue):
        self.rawon()
        self.val(hue)

    def brightness(self,bri):
        self.rawon()
        self.val(bri)

class iboxlight(milight3light):
    def __init__(self, parent, hue=-1, val=0):
        debugprint ("Initialising ibox: Hue: "+str(hue)+" Val: "+str(val))
        self.parent = parent
        self.zone = 1
        self._hue = hue
        self._val = val

    def rawon(self):
        self.send("31 00 00 00 03 03 00 00 00")

    def rawoff(self):
        self.send("31 00 00 00 03 04 00 00 00")

    def hue(self,hue):
        if hue >=0 and hue <= 255:
            val = " " + format(hue, "02X")[:2]
            self.send("31 00 00 00 01"+val+val+val+val)
            if self._hue == -1:
                self.val(zone,self._val)
            self._hue = hue

    def val(self,bri):
        if bri >=0 and bri <= 100:
            val = format(bri, "02X")[:2]
            self.send("31 00 00 00 02 "+val+" 00 00 00")
            self._val = bri+1

    def on(self, val=None):
        self.rawon()
        if self._hue == -1:
            self.temp(self._tmp)
        else:
            self.hue(self._hue)
        if val is None:
            if self._val == 0:
                self.val(0)
            else:
                self.val(abs(self._val)-1)
        else:
            self.val(val)
        
    def off(self):
        self.send("31 00 00 00 02 00 00 00 00") # Set Brightness to zero before turn off
        self.rawoff()
        self._val = -1

    def white(self):
        self.rawon()
        self.send("31 00 00 00 05 00 00 00 00")
        if self._hue != -1:
            self.val(self._val-1)
            self._hue = -1

    def colour(self,hue,val=None):
        self.rawon()
        self.hue(hue)
        if val is None:
            self.val(self._val)
        else:
            self.val(val)

    def status(self):
        print "Zone       : iBox Light"
        print "Hue        :",self._hue
        print "Saturation : "+str(self._sat)+"%"
        print
        

class rgbww(milight3light):
    def __init__(self, parent, zone, hue=-1, sat=100, val=0, tmp=0):
        debugprint ("Initialising zone: "+str(zone)+" Hue: "+str(hue)+" Sat: "+str(sat)+" Val: "+str(val)+" Temp: "+str(tmp))
        self.parent = parent
        self.zone = zone
        self._hue = hue
        self._sat = sat
        self._val = val
        self._tmp = tmp

    def rawon(self):
        self.send("31 00 00 08 04 01 00 00 00")

    def rawoff(self):
        self.send("31 00 00 08 04 02 00 00 00")

    def hue(selfhue):
        if hue >=0 and hue <= 255:
            val = " " + format(hue, "02X")[:2]
            self.send("31 00 00 08 01"+val+val+val+val)
            if self._hue == -1:
                self.val(zone,self._val)
            self._hue = hue
        
    def sat(self,sat):
        if sat >=0 and sat <= 100:
            val = format(sat, "02X")[:2]
            self.send("31 00 00 08 02 "+val+" 00 00 00")
            self._sat = sat

    def val(self,bri):
        if bri >=0 and bri <= 100:
            val = format(bri, "02X")[:2]
            self.send("31 00 00 08 03 "+val+" 00 00 00")
            self._val = bri+1

    def temp(self,temp):
        val = format(temp, "02X")[:2]
        self.send("31 00 00 08 05 "+val+" 00 00 00")
        self._tmp = temp

    def hsv(self,hue,sat,val):
        self.hue(hue)
        self.sat(sat)
        self.val(val)

    # Basic Commands

    def on(self, val=None):
        self.rawon()
        if self._hue == -1:
            self.temp(self._tmp)
        else:
            self.hue(self._hue)
            self.sat(self._sat)
        if val is None:
            if self._val == 0:
                self.val(0)
            else:
                self.val(abs(self._val)-1)
        else:
            self.val(val)
        
    def off(self):
        self.send("31 00 00 08 03 00 00 00 00") # Set Brightness to zero before turn off
        self.rawoff()
        self._val = -1
        
    def night(self):
        self.send("31 00 00 08 04 05 00 00 00")
        self._val = 0
        self._hue = -1
        self._tmp = 100

    def white(self):
        self.rawon()
        self.send("31 00 00 08 05 64 00 00 00")
        if self._hue != -1:
            self.val(self._val-1)
            self._hue = -1

    def saturation(self,sat):
        self.rawon()
        self.val(sat)

    def temperature(self,temp):
        self.rawon()
        self.tmp(temp)

    def colour(self,hue,sat,val):
        self.rawon()
        self.hsv(hue,sat,val)

    def status(self):
        print "Zone       :",self.zone
        print "Hue        :",self._hue
        print "Saturation : "+str(self._sat)+"%"
        print "Value      : "+str(self._val-1)+"%"
        print "Temperature: "+str(self._tmp)+"%"
        print

    # Fancy Internal Commands

    def fadetemp(self,sourcetemp,desttemp,speed=DEFAULT_SPEED):
        if sourcetemp != desttemp:
            if sourcetemp < desttemp:
                speed = abs(speed)
            elif sourcetemp > desttemp:
                speed = -abs(speed)
        
            for n in range(sourcetemp,desttemp,speed):
                self.temp(n)
        self.temp(desttemp)

    def fadewhite(self,sourceval,destval,sourcetemp,desttemp,speed=DEFAULT_SPEED):
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

            self.val(val)
            self.temp(temp)

        self.val(destval)
        self.temp(desttemp)

    def whitetohsv(self,sourceval,desthue,destsat,destval, speed=DEFAULT_SPEED):
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
        self.hsv(desthue,sat,sourceval)
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
            self.sat(sat)
            self.val(val)

    def hsvtowhite(self,sourcehue,sourcesat,sourceval,destval,temp=None, speed=DEFAULT_SPEED):
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
        self.hsv(sourcehue,sat,val)
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
            self.sat(sat)
            self.val(val)
        self.white()
        self.val(destval)
        if temp is not None:
            self.temp(temp)

    def hsvtohsv(self,sourcehue,sourcesat,sourceval,desthue,destsat,destval,speed=DEFAULT_SPEED):
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

        self.hsv(hue,sat,val)
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
            self.hsv(hue,sat,val)

#   Fancy commands

    def fadetocolour(self,hue,sat,val,speed=DEFAULT_SPEED):
        self.rawon()
        if self._hue == -1:
            self.whitetohsv(self._val-1,hue,sat,val,speed)
        else:
            self.hsvtohsv(self._hue,self._sat,self._val-1,hue,sat,val,speed)

    def fadetotemp(self,temp,speed=DEFAULT_SPEED):
        if self._hue == -1 and self._val > 0:
            self.fadetemp(self._tmp,temp,speed)
        else:
            self.hsvtowhite(self._hue,self._sat,self._val-1,val, temp, speed)

    def fadetowhite(self,val,temp=None,speed=DEFAULT_SPEED):
        self.rawon()        
        if self._hue == -1:
            if self._val == 0:
                self.rawon()
                self.temp(100)
            if temp is None:
                self.fadeval(self._val,val,speed)
            else:
                self.fadewhite(self._val-1,val,self._tmp,temp,speed)
        else:
            self.hsvtowhite(self._hue,self._sat,self._val-1,val, temp, speed)

