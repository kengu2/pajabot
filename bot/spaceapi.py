import zerorpc

class SpaceAPI(object):
    def bad(self):
        raise Exception("Connection problem on rpc?")

    def __init__(self, url):
        print "SpaceAPI connecting to " + url
        self.c = zerorpc.Client()
        self.c.connect(url)

    def updateStatus(self, labOpen, topic):
        print "Setting lab open " + str(labOpen) + " and topic " + topic
        self.c.updateStatus(labOpen, topic)
        print "Update ok"

