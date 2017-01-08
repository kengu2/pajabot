#!/usr/bin/python
# -*- coding: utf-8 -*-
#import wiringpi2
import time
import sys
import urllib2

PIN=15

LIGHT_CUT=700

#wiringpi2.wiringPiSetupSys()
#wiringpi2.pinMode(PIN,0)

class IiOo():
    def __init__(self):
        pass

    def checkLights(self):
        
        try:
            conn = urllib2.urlopen("https://api.thingspeak.com/channels/196110/fields/2/last")
            response = conn.read()
#    print "http status code=%s" % (conn.getcode())
#    print response
#    print LIGHT_CUT<response
            conn.close()
            return LIGHT_CUT<int(response)
        except:
            pass
