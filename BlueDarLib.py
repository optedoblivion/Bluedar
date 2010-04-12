#!/usr/bin/python
# coding: utf-8

"""
    BlueDar Library
    
"""

__version__ = "0.0.1"

import os
import sys
import signal
import time
import threading
from xmlrpclib import Server

try:
    import bluetooth
except:
    print "You need the bluetooth package installed!"
    sys.exit(1)

try:
    import _bluetooth as bluez
except:
    try:
        import bluetooth._bluetooth as bluez
    except:
        print "Please install bluez and python-pybluez"
        sys.exit(1)

CONFIG_FILE = ".BlueDar"
CONFIG = os.popen("echo $HOME")
CONFIG = str(CONFIG.next())[:-1]
CONFIG = CONFIG + "/" + CONFIG_FILE

class BlueDar(threading.Thread):

    macAddress = None
    lastDistance = 0
    unlockDistance = 7
    lockDistance = 4
    updateInterval = 5
    lockCommand = None
    unlockCommand = None
    proximityCommand = None
    terminateFlag = False
    verbose = False
    status = "unlocked"

    sock = None
    ringbuffer_size = 1
    ringbuffer = [-254] * ringbuffer_size
    ringbuffer_pos = 0

    configFile = CONFIG

    def log(self, str):
        print str

    def __init__(self):
        threading.Thread.__init__(self, name="UnderLayer")
        if self.verbose:
            self.log("Class has been initialized...\n")

    def getProximity(self):
        
        try:
            s = Server("http://127.0.0.1:54000")
            signal = s.getProximity(self.macAddress)
        except:
            signal = None
            
        return signal

    def execute(self, command):
        if not command:
            return
        if self.verbose:
            self.log("Executing: %s" % command)
        os.system(command)

    def getNearbyDevices(self):
        ret_tab = list()
        if self.verbose:
            self.log("Scanning for devices...")
        try:
            nearby_devices = bluetooth.discover_devices()
        except Exception, data:
            self.log("Failed.\n")
            self.log("Recieved: %s - %s\n"%(data[0],data[1]))
            sys.exit(1)
        if self.verbose:
            self.log("Done.\n")

        for bdaddr in nearby_devices:
            ret_tab.append([str(bdaddr),str(bluetooth.lookup_name( bdaddr ))])
        return ret_tab

    def config(self):
        devices = self.getNearbyDevices()
        if len(devices) < 1:
            self.log('No devices found!\n')
            sys.exit(1)
        self.finalConfig(devices)

    def finalConfig(self, devices=[]):
        config = {}
        iter = 0
        self.log("\nNearby Devices:\n\n")
        for device in devices:
            iter+=1
            self.log("%s) %s - %s\n" % (iter, device[1], device[0]))
        cmd = raw_input('\nSelect Device: ')
        try:
      	    cmd = int(cmd)
    	except:
            self.log("Invalid Device Number!\n")
            self.finalConfig(devices)
        if cmd == 0 or cmd > iter:
            self.log("Invalid Device Number!\n")
            self.finalConfig(devices)
        else:
            config["macAddress"] = devices[cmd-1][0]

        LockDist = raw_input("Enter distance to lock: ")
        interval = raw_input("Interval (seconds): ")
    	try:
            LockDist = int(LockDist)
    	    interval = int(interval)
        except:
            self.log("You must enter numbers!")
    	    self.finalConfig(devices)

        config["lockDistance"] = LockDist
        config["unlockDistance"] = LockDist-10
        config["updateInterval"] = interval

        config['lockCommand'] = ""
        config['unlockCommand'] = ""
        config['proximityCommand'] = ""

        configFile = open(self.configFile, 'wb')
        configFile.write("# Bluedar Config")
        for key in config.keys():
            configFile.write("%s=%s"%(key,config[key]))
	    configFile.write("\n")
        configFile.close()
        self.log("Config file has been written...\n\n")

    def setupConfig(self):
        # Load Config
        if os.path.exists(self.configFile):
            config = open(self.configFile, 'rb')
            data = config.readlines()
            for line in data:
                if not str(line)[0] == "#":
                    keyVal = str(line).split('=')
                    if self.verbose:
                        self.log('self.%s = "%s"\n' %
                                  (keyVal[0], str(keyVal[1]).replace('\n','')))
                    exec'self.%s="%s"'%(keyVal[0], str(keyVal[1]).replace('\n',''))
            config.close()
        else:
            self.log("You must create a config file.\n\tHint: %s -c\n"%sys.argv[0])

    def run(self):

        while not self.terminateFlag:

            self.setupConfig()

            distance = self.getProximity()
            self.lastDistance = distance
            if self.verbose:
                print "Signal: %s"%distance

            if distance == 0:distance-=1

            if distance:

                if abs(int(distance)) >= int(self.lockDistance):
                    if self.status == "unlocked":
                        self.execute(self.lockCommand)
                        self.status = "locked"

                if abs(int(distance)) <= int(self.unlockDistance):
                    if self.status == "locked":
                        self.execute(self.unlockCommand)
                        self.status = "unlocked"
            else:
                if self.status == "unlocked":
                    self.execute(self.lockCommand)
                    self.status = "locked"

            time.sleep(float(self.updateInterval))

if __name__=='__main__':

    signal.signal(signal.SIGINT, signal.SIG_DFL)

    blue = BlueDar()

    if len(sys.argv) > 1:
        for arg in range(1,len(sys.argv)):
            if str(sys.argv[arg])[0] != '-':
                blue.log("Invalid option '%s'.\n" % sys.argv[arg])
                sys.exit(1)
            else:
                if str(sys.argv[arg])[1] == 'c':
                    blue.log("Calling configuration manager...\n")
                    blue.config()
                elif str(sys.argv[arg])[1] == 'v':
                    blue.verbose = True
                else:
                    blue.log("Invalid option '%s'.\n" % sys.argv[arg])
                    sys.exit(1)
    
    blue.setupConfig()
    if blue.verbose:
        blue.log("Running daemon...\n")
    blue.run()

