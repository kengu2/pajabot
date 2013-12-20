#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
from PIL import Image,ImageStat

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
		self.removeShot()
		return pixelsum > 50

	def takeShot(self):
                os.system('/home/pi/pajabot/scripts/takeshot.sh')

	def removeShot(self):
                os.system('/home/pi/pajabot/scripts/removeshot.sh')

	def uploadShot(self):
                os.system('/home/pi/pajabot/scripts/uploadshot.sh')

	def getPixelSum(self):
                im = Image.open("/tmp/shot.jpg")
                stat = ImageStat.Stat(im)
                pixelsum = stat.mean[0]+stat.mean[1]+stat.mean[2] 
		return pixelsum

