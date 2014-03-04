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
import glob
import imp

from irc.bot import ServerSpec
from irc.bot import SingleServerIRCBot

from rpi_camera import RPiCamera

import subprocess


# TODO: 
# - Proper configuration
# - Separate GPIO to different process
# - Epic stuff


commands = {}

def scan():
    commands.clear()
    for moduleSource in glob.glob ('plugins/*.py'):
        name = moduleSource.replace ('.py','').replace ('\\','/').split ('/')[1].upper()
        handle = open (moduleSource)
        module = imp.load_module ('COMMAND_'+name, handle, ('plugins/'+moduleSource), ('.py', 'r', imp.PY_SOURCE))
        commands[name] = module
scan()

print commands
print commands.items()
print commands['PRINTTERI'].info()
commands['PRINTTERI'].info()


class PajaBot(SingleServerIRCBot):
    def __init__(self):

        scan()
         
        config = ConfigParser.ConfigParser()

        configfile = '/home/pi/pajabot/bot.conf' 
        if (os.path.isfile('/home/pi/pajabot/local.conf')):
            configfile = '/home/pi/pajabot/local.conf'

        config.read(configfile)

        self.server = config.get("bot","server")
        self.ircchannel = config.get("bot","channel")
        self.nick = config.get("bot","nick")
        self.realname = config.get("bot","realname")
        self.shoturl = config.get("bot","shoturl")

        self.messageasaction = config.getboolean("bot","messageasaction")
        self.vaasa = config.getboolean("bot","vaasa")
        self.printer_ip = config.get("bot","printer")


        try:
            self.password = config.get("bot","password")
        except ConfigParser.NoOptionError:
            print "no password"
            self.password = ''

        try:
            self.rss_url = config.get("vaasa","rss")
        except ConfigParser.NoOptionError:
            print "not in vaasa?"
            self.rss_url = ''

        self.rss_timestamp = ''

        print "-- config --"
        print self.server
        print self.ircchannel
        print self.nick
        print self.realname
        print self.messageasaction
        print self.vaasa
        print self.rss_url
        print self.password
        print self.printer_ip
        print "-- end config --"


        spec = ServerSpec(self.server)
        SingleServerIRCBot.__init__(self, [spec], self.nick, self.realname)
        self.reconnection_interval = 60
        self.running = True
        self.channel = self.ircchannel
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
            if (self.vaasa): self.read_feed()
            try:
                self.ircobj.process_once(0.2)
            except UnicodeDecodeError:
                print 'Somebody said something in non-utf8'
#                                traceback.print_exc(file=sys.stdout)
            except irc.client.ServerNotConnectedError:
                print 'Not connected. Can not do anything atm.'
            time.sleep(0.5)


    def read_feed(self):
        c = self.connection
        global rss_timestamp

        rssfeed = feedparser.parse(self.rss_url)
        if len(rssfeed.entries)>0:
            latest = rssfeed.entries[len(rssfeed.entries)-1]
            
            if latest.id in self.rss_timestamp:
                variable = 2           
            else: 
                self.rss_timestamp = latest.id
                try:
                    self.say("door opened by " + latest.title)
                    print "new openings " + latest.title
                except:
                    print "not connected"




    def checkLights(self):
        self.lightCheck -= 1
        if self.lightCheck < 0:
#            print 'Checking lights..'
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
        if self.messageasaction:
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
        if (self.password!=''): c.privmsg("nickserv", "IDENTIFY " + self.password)


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

    def on_disconnect(self, c, e):
        raise SystemExit() 

    def on_pubmsg(self, c, e):
#        cmd = e.arguments[0]
        cmd = e.arguments()[0].split()[0]

        if cmd[0] == "!":
            cmd = cmd[1:].upper()
            if commands.has_key(cmd):
                commands[cmd].index(self, c, e)

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
            ping_response = subprocess.Popen(["/bin/ping", "-c1", "-w2", self.printer_ip], stdout=subprocess.PIPE).stdout.read()
            if ('rtt' in ping_response):
                self.say('printer is online')
            else:
                self.say('printer is offline')
            print('p: ' + str(ping_response))

        if (cmd=='!printteri'):
            commands['PRINTTERI'].index(self, c,e)


        if cmd=='!shot':
            self.camera.takeShotCommand()
            c.privmsg(self.channel, self.shoturl + ('' if self.lightStatus else ' (pretty dark, eh)'))
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
        subprocess.Popen("/home/pi/pajabot/bot/pajabot.py", shell=False)
        SingleServerIRCBot.die(self, 'By your command')
        exit("updating")


bot = PajaBot()

