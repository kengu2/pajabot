import six
import os
import time
import sys
import irc.client
import irc.bot
import traceback
from irc.bot import ServerSpec
from irc.bot import SingleServerIRCBot
from PIL import Image,ImageStat

import RPi.GPIO as GPIO
class PajaBot(SingleServerIRCBot):
        def __init__(self):
                spec = ServerSpec('irc.freenode.net')
                SingleServerIRCBot.__init__(self, [spec], 'pajabot', '5w Pajabotti')
                self.running = True
                self.channel = '#5w'
                self.doorpin = 11
                self.doorStatus = GPIO.input(self.doorpin)
                self._connect()
                while(self.running):
                        newDs = GPIO.input(self.doorpin)
                        if newDs is not self.doorStatus:
                                self.doorStatus = newDs
                                self.sayDoorStatus()
                        try:
                                self.ircobj.process_once(0.2)
                        except UnicodeDecodeError:
                                traceback.print_exc(file=sys.stdout)
                        time.sleep(0.5)

        def on_welcome(self, c, e):
                c.join(self.channel)

        def sayDoorStatus(self):
                c = self.connection
                ds = self.doorStatus
                if ds == GPIO.LOW:
                        dss = 'auki'
                else:   
                        dss = 'kiinni'
                dss = 'Pajan ovi on ' + dss
                c.privmsg(self.channel, dss)

        def on_pubmsg(self, c, e):
                cmd = e.arguments[0]
                print 'Komento: ' + cmd
                if cmd=='!kuole':
                        self.running = False
                        SingleServerIRCBot.die(self, 'By your command')
                if cmd=='!ovi':
                        self.sayDoorStatus()
                if cmd=='!shot':
                        os.system('/home/pi/takeshot.sh')
                        im = Image.open("/tmp/shot.jpg")
                        stat = ImageStat.Stat(im)
                        pixelsum = stat.mean[0]+stat.mean[1]+stat.mean[2] 
                        #print pixelsum
                        #the true magicish
                        if pixelsum<10:
                            ss = 'Pretty dark, eh'
                        else:
                            ss = 'Pajalla tapahtuu'
                        ss += ' (' + str(round(pixelsum)) + '): http://5w.fi/shot.jpg'

                        c.privmsg(self.channel, ss)

                        os.system('/home/pi/removeshot.sh')


        def _dispatcher(self, c, e):
                eventtype = e.type
                source = e.source
                if source is not None:
                        source = str(source)
                else:
                        source = ''
                print "E:" + str(source) + ", " + str(eventtype) + ", " + str(e.arguments)
                SingleServerIRCBot._dispatcher(self, c, e)

GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.IN)

bot = PajaBot()

GPIO.cleanup()

