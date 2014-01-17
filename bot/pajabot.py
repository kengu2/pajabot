#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import six
import time
import datetime
import irc.client
import irc.bot
import traceback
import os
import ConfigParser

from irc.bot import ServerSpec
from irc.bot import SingleServerIRCBot

from rpi_camera import RPiCamera

from subprocess import Popen


# TODO: 
# - Proper configuration
# - Separate GPIO to different process
# - Epic stuff

config = ConfigParser.ConfigParser()
config.read('/home/pi/pajabot/bot.conf')

server = config.get("bot","server")
ircchannel = config.get("bot","channel")
nick = config.get("bot","nick")
realname = config.get("bot","realname")

messageasaction = False

print server
print ircchannel
print nick
print realname

class PajaBot(SingleServerIRCBot):
        def __init__(self):
                spec = ServerSpec(server)
                SingleServerIRCBot.__init__(self, [spec], nick, realname)
                self.running = True
                self.channel = ircchannel
		self.doorStatus = None
		self.camera = RPiCamera()
		self.lightStatus = self.camera.checkLights()
                self._connect()
		self.lightCheck = 0 # Check only every N loops
		self.statusMessage = "Hello world"
		self.timestamp = datetime.datetime.now()

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
				newTimestamp = datetime.datetime.now()
				timeDelta = str(newTimestamp - self.timestamp).split('.')[0]
				lss = 'Pajan valot ' + ('sammutettiin (valot päällä ' if not newLights else 'sytytettiin (pimeyttä kesti ') + timeDelta + ')'
				self.say(lss)
				self.lightStatus = newLights
				self.timestamp = newTimestamp
				self.updateStatus()
			self.lightCheck = 120

	def say(self, text):
		if messageasaction:
			self.connection.action(self.channel, text)
		else:
			self.connection.privmsg(self.channel, text)
			

	def updateStatus(self):
		openstatus = ('true' if self.lightStatus else 'false')
		self.statusMessage = ('The lab is manned' if self.lightStatus else 'No one here atm')
		print 'Updating status: ' + openstatus + ', ' + self.statusMessage
		os.system('/home/pi/pajabot/scripts/updatestatus.sh ' + openstatus + ' "' + self.statusMessage + '"')
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
                self.say(dss)

        def on_pubmsg(self, c, e):
                cmd = e.arguments[0]
                if cmd=='!kuole':
                        self.running = False
                        SingleServerIRCBot.die(self, 'By your command')
                if cmd=='!ovi':
                        self.sayDoorStatus()
                if cmd=='!valot':
                        self.say('Pajan valot ovat ' + ('päällä' if self.lightStatus else 'pois päältä'))
                if cmd=='!shot':
			self.camera.takeShotCommand()
	                c.privmsg(self.channel, 'http://5w.fi/shot.jpg' + ('' if self.lightStatus else ' (pajalla pimeää)'))
		if cmd=='!gitpull':
	                os.system('/home/pi/pajabot/scripts/gitpull.sh')
	                c.privmsg(self.channel, 'Pullattu gitistä, käynnistyn uudestaan..')
			self.restart_program()
                if cmd=='!update':
 	                self.updateStatus()
	                c.privmsg(self.channel, 'Done')

        def _dispatcher(self, c, e):
                eventtype = e.type
                source = e.source
                if source is not None:
                        source = str(source)
                else:
                        source = ''
                SingleServerIRCBot._dispatcher(self, c, e)

	def restart_program(self):

		print ('Restarting')
		Popen("/home/pi/pajabot/bot/pajabot.py", shell=False)
		SingleServerIRCBot.die(self, 'By your command')
		exit("updating")


bot = PajaBot()

