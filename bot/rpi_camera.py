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
                if pixelsum<10:
                    ss = 'Pretty dark, eh'
                else:
                    ss = 'Pajalla tapahtuu'
                ss += ' (' + str(round(pixelsum)) + '): http://5w.fi/shot.jpg'

                c.privmsg(self.channel, ss)

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

