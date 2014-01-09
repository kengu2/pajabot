#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import six
import time
import irc.client
import irc.bot
import traceback
import os

from irc.bot import ServerSpec
from irc.bot import SingleServerIRCBot

from rpi_camera import RPiCamera

# TODO: 
# - Proper configuration
# - Separate GPIO to different process
# - Epic stuff

class PajaBot(SingleServerIRCBot):
        def __init__(self):
                spec = ServerSpec('irc.freenode.net')
                SingleServerIRCBot.__init__(self, [spec], 'pajabot', '5w Pajabotti')
                self.running = True
                self.channel = '#5w'
		self.doorStatus = None
		self.camera = RPiCamera()
		self.lightStatus = self.camera.checkLights()
                self._connect()
		self.lightCheck = 0 # Check only every N loops
                while(self.running):
			self.checkLights()
                        try:
                                self.ircobj.process_once(0.2)
                        except UnicodeDecodeError:
                                traceback.print_exc(file=sys.stdout)
                        time.sleep(0.5)

	def checkLights(self):
		self.lightCheck -= 1
		if self.lightCheck < 0:
			print 'Checking lights..'
			newLights = self.camera.checkLights()
			if newLights is not self.lightStatus:
				lss = 'Pajan valot ' + ('sammutettiin' if not newLights else 'sytytettiin')
				self.connection.privmsg(self.channel, lss)
				self.lightStatus = newLights
				self.updateStatus()
			self.lightCheck = 120

	def updateStatus(self):
		openstatus = "false"
		statusmessage = "Nobody is at lab"
		if self.lightStatus:
			openstatus = "true"
			statusmessage = "The lab is manned"
		os.system('/home/pi/pajabot/scripts/updatestatus.sh ' + openstatus + ' "' + statusmessage + '"')
		self.camera.takeShotCommand()

        def on_welcome(self, c, e):
                c.join(self.channel)

        def sayDoorStatus(self):
                c = self.connection
                ds = self.doorStatus
                dss = 'rikki'
		if ds is False:
                        dss = 'auki'
                if ds is True:
                        dss = 'kiinni'
                dss = 'Pajan ovi on ' + dss
                c.privmsg(self.channel, dss)

        def on_pubmsg(self, c, e):
                cmd = e.arguments[0]
                print 'Komento: ' + str(cmd)
                if cmd=='!kuole':
                        self.running = False
                        SingleServerIRCBot.die(self, 'By your command')
                if cmd=='!ovi':
                        self.sayDoorStatus()
                if cmd=='!valot':
                        c.privmsg(self.channel, 'Pajan valot ovat ' + ('päällä' if self.lightStatus else 'pois päältä'))
                if cmd=='!shot':
			self.camera.takeShotCommand()
	                c.privmsg(self.channel, 'http://5w.fi/shot.jpg')
		if cmd=='!gitpull':
	                os.system('/home/pi/pajabot/scripts/gitpull.sh')
	                c.privmsg(self.channel, 'Pullattu gitistä, käynnistyn uudestaan..')
			self.restart_program()

        def _dispatcher(self, c, e):
                eventtype = e.type
                source = e.source
                if source is not None:
                        source = str(source)
                else:
                        source = ''
                print "E:" + str(source) + ", " + str(eventtype) + ", " + str(e.arguments)
                SingleServerIRCBot._dispatcher(self, c, e)

	def restart_program(self):
		python = sys.executable
		#print "Executing: " + python
                self.running = False
		SingleServerIRCBot.die(self, 'By your command')
		os.execl("/home/pi/pajabot/bot/pajabot.py")



bot = PajaBot()

