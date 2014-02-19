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
import feedparser

from irc.bot import ServerSpec
from irc.bot import SingleServerIRCBot

from rpi_camera import RPiCamera

from subprocess import Popen


# TODO: 
# - Proper configuration
# - Separate GPIO to different process
# - Epic stuff

config = ConfigParser.ConfigParser()

configfile = '/home/pi/pajabot/bot.conf' 
if (os.path.isfile('/home/pi/pajabot/local.conf')):
	configfile = '/home/pi/pajabot/local.conf'

config.read(configfile)

server = config.get("bot","server")
ircchannel = config.get("bot","channel")
nick = config.get("bot","nick")
realname = config.get("bot","realname")
shoturl = config.get("bot","shoturl")

messageasaction = config.getboolean("bot","messageasaction")
vaasa = config.getboolean("bot","vaasa")

try:
	password = config.get("bot","password")
except ConfigParser.NoOptionError:
	print "no password"
	password = ''

try:
	rss_url = config.get("vaasa","rss")
except ConfigParser.NoOptionError:
	print "not in vaasa?"
	rss_url = ''

rss_timestamp = ''

print "-- config --"
print server
print ircchannel
print nick
print realname
print messageasaction
print vaasa
print rss_url
print password
print "-- end config --"

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
                self.updateStatus()

                while(self.running):
                        self.checkLights()
                        if (vaasa): self.read_feed()
                        try:
                                self.ircobj.process_once(0.2)
                        except UnicodeDecodeError:
				print 'Somebody said something in non-utf8'
#                                traceback.print_exc(file=sys.stdout)
			except irc.client.ServerNotConnectedError:
				print 'Not connected. Cant do anything atm.'

                        time.sleep(0.5)


	def read_feed(self):
		c = self.connection
		global rss_timestamp

		rssfeed = feedparser.parse(rss_url)
		if len(rssfeed.entries)>0:
			latest = rssfeed.entries[len(rssfeed.entries)-1]
            
			if latest.id in rss_timestamp:
				variable = 2           
			else: 
				rss_timestamp = latest.id
				try:
					self.say("door opened by " + latest.title)
					print "new openings " + latest.title
				except:
					print "not connected"




	def checkLights(self):
		self.lightCheck -= 1
		if self.lightCheck < 0:
#			print 'Checking lights..'
			newLights = self.camera.checkLights()
			if newLights is not self.lightStatus:
				newTimestamp = datetime.datetime.now()
				timeDelta = str(newTimestamp - self.timestamp).split('.')[0]
				lss = 'lights ' + ('went off (lights were illuminated for ' if not newLights else 'on (darkness had fallen for ') + timeDelta + ')'
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
                if (password!=''): c.privmsg("nickserv", "IDENTIFY " + password)


        def sayDoorStatus(self):
                c = self.connection
                ds = self.doorStatus
                dss = 'broken'
		if ds is False:
                        dss = 'open'
                if ds is True:
                        dss = 'closed'
                dss = 'door is ' + dss
                self.say(dss)

        def on_nicknameinuse(self, c, e):
            c.nick(c.get_nickname() + "_")


        def on_pubmsg(self, c, e):
                cmd = e.arguments[0]
                if cmd=='!kuole':
                        self.running = False
                        SingleServerIRCBot.die(self, 'By your command')
                if (cmd=='!ovi') or (cmd=='!door'):
                        self.sayDoorStatus()
                if (cmd=='!valot') or (cmd=='!lights'):
                        self.say('lights are ' + ('on' if self.lightStatus else 'off'))
                if (cmd=='!checksum') or (cmd=='!checksum'):
                        self.say('pixelvar: ' + str(self.camera.checkSum()))
                if (cmd=='!printer') or (cmd=='!tulostin'):
                        ping_response = subprocess.Popen(["/bin/ping", "-c1", "-w100", "8.8.8.8"], stdout=subprocess.PIPE).stdout.read()
                        self.say('p: ' + str(ping_response))



                if cmd=='!shot':
			self.camera.takeShotCommand()
	                c.privmsg(self.channel, shoturl + ('' if self.lightStatus else ' (pretty dark, eh)'))
		if cmd=='!gitpull':
	                os.system('/home/pi/pajabot/scripts/gitpull.sh')
	                c.privmsg(self.channel, 'Pulled from git, restarting..')
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

