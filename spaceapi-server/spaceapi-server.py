import zerorpc
import re
import time

with open('spaceapi.json.template','r') as f:
    templatefile = f.read();

print templatefile

class SpaceAPI(object):
    def updateStatus(self, labOpen, topic):
        print "Set lab open " + str(labOpen) + " and topic " + topic
        updatedfile2 = re.sub("STATUS_OPEN", str(labOpen) , templatefile)
        updatedfile = re.sub("STATUS_LASTCHANGE", str(int(time.time())), updatedfile2)
        outfile = open('spaceapi.json', 'w')
        outfile.write(updatedfile)
        outfile.close
        return "Update ok"

s = zerorpc.Server(SpaceAPI())
s.bind("tcp://0.0.0.0:4242")
s.run()
