#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import traceback
from PIL import Image,ImageStat
import requests
from StringIO import StringIO

url = "http://tunkki1.lan/cam1/lastsnap.jpg"

class RPiCamera():
    def __init__(self):
        pass

    def takeShotCommand(self):
        self.takeShot()
        self.uploadShot()
        self.removeShot()

    def checkLights(self):
        self.takeShot()
        pixelsum = self.getPixelSum()
#        print "checkLights: pixelsum is " + str(pixelsum)
        self.removeShot()
        return pixelsum > 500

    def takeShot(self):
        os.system('/home/ovi/pajabot/scripts/takeshot.sh')

    def removeShot(self):
        os.system('/home/ovi/pajabot/scripts/removeshot.sh')

    def uploadShot(self):
        os.system('/home/ovi/pajabot/scripts/uploadshot.sh')

    def getPixelSum(self):
        try:
            response = requests.get(url)
            im = Image.open(StringIO(response.content))
            im = im.crop((90,50,220,70))
            #im = Image.open("/tmp/shot.jpg")
            stat = ImageStat.Stat(im)
            pixelsum = stat.mean[0]+stat.mean[1]+stat.mean[2] 
            return pixelsum
        except IOError:
            print "cannot identify image file"
            traceback.print_exc()
            return -1

    def checkSum(self):
#        self.takeShot()
#        response = requests.get(url)
#        im = Image.open(StringIO(response.content))
#        im = Image.open("/tmp/shot.jpg")
#        stat = ImageStat.Stat(im)
#        pixelsum = stat.mean[0]+stat.mean[1]+stat.mean[2] 
#        pixelvar = stat.var[0]+stat.var[1]+stat.var[2]
#        self.uploadShot()
#        self.removeShot()
#        return pixelsum
        return self.getPixelSum()

