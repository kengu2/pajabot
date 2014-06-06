#!/usr/bin/python
# -*- coding: utf-8 -*-
#import wiringpi2
import time
import sys

PIN=15

#wiringpi2.wiringPiSetupSys()
#wiringpi2.pinMode(PIN,0)

class IiOo():
    def __init__(self):
        pass

    def checkLights(self):
        with open('/sys/class/gpio/gpio15/value') as f:
            status = f.read(1)
        print status
        return not (bool(int(status)))
