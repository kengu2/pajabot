import subprocess

def index (self, connection, event):
    ping_response = subprocess.Popen(["/bin/ping", "-c1", "-w2", self.printer_ip], stdout=subprocess.PIPE).stdout.read()
    if ('rtt' in ping_response):
        self.say('printer is online')
    else:
        self.say('printer is offline')
    print('p: ' + str(ping_response))

