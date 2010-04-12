#! /usr/bin/python

__author__="reaper"
__date__ ="$Mar 25, 2009 11:02:40 PM$"

import pyrssi
from DocXMLRPCServer import DocXMLRPCServer

class BlueDarD(DocXMLRPCServer):

    terminateFlag = False

    def __init__(self):
        DocXMLRPCServer.__init__(self, ('0.0.0.0', 54000), logRequests=False)
        self.set_server_name("RSSI Proximity")
        self.register_function(self.getProximity)
        
    def getProximity(self, macAddress=None):

        if not macAddress:
            return macAddress

        try:
            signal = pyrssi.read_rssi(macAddress)
            if int(signal) > 0:
                signal = None
        except:
            signal = None

        return signal

    def run(self):
        self.terminateFlag = False
        while not self.terminateFlag:
            self.handle_request()

if __name__ == "__main__":
    main = BlueDarD()
    main.run()
