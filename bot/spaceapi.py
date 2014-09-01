import zerorpc

c = zerorpc.Client()
c.connect("tcp://127.0.0.1:4242")
print c.updateStatus(True, "testing")

class SpaceAPI(object):
    def __init__(self, url):
	print "SpaceAPI connecting to " + url
	c = zerorpc.Client()
	c.connect(url)

    def updateStatus(self, labOpen, topic):
	print "Setting lab open " + str(labOpen) + " and topic " + topic
	c.updateStatus(labOpen, topic)
        print "Update ok"

