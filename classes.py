import sys

class Config:
    def __init__(self, path):
        self.path = path

class ServerHandler:
    def __init__(self, config):
        self.config = config
        self.serversockets = []
        self.clients = {} #socket -> client
        self.remotesockets = []
        self.readingfromsockets = []
        self.selectlist = [sys.stdin]
        self.run = True

    def sigint(self, message):
        for socket in self.clients:
            socket.send("ERROR :Closing link: " + str(self.clients[socket]) + " (Server shutdown: " + message + ")\r\n")
            self.clientdisconnected(socket)
    
    def acceptconnection(self, serversocket):
        socket, (remotehost, remoteport) = serversocket.accept()
        self.remotesockets.append(socket)
        self.clients[socket] = Client(socket, serversocket, remotehost, remoteport)
        self.selectlist.append(socket)
        #print self.remotesockets
    
    def readline(self, stream): #input from a socket or console
        if stream == sys.stdin: #console
            line = sys.stdin.readline()
        else: #a socket
            self.readingfromsockets.append(stream)
            try:
                line = ""
                while True:
                    line += stream.recv(1)
                    if len(line) >= 2 and line[-2:] == "\r\n":
                        line = line[:-2]
                        break
            except:
                self.clientdisconnected(stream)
                if stream in self.readingfromsockets:
                    self.readingfromsockets.remove(stream)
                return
            if stream in self.readingfromsockets:
                self.readingfromsockets.remove(stream)
        self.processline(stream, line)
    
    def processline(self, stream, line):
        if stream in self.clients:
            client = self.clients[stream]
            print "Line from " + str(client) + ": " + line
        elif stream == sys.stdin:
            print line
    
    def clientdisconnected(self, socket):
        if socket in self.selectlist:
            self.selectlist.remove(socket)
        if socket in self.remotesockets:
            self.remotesockets.remove(socket)
        if socket in self.readingfromsockets:
            self.readingfromsockets.remove(socket)
        if socket in self.clients.values():
            del self.clients[socket]
        socket.close()
    
    def addserversocket(self, serversocket):
        self.serversockets.append(serversocket)
        self.selectlist.append(serversocket)

class Client:
    def __init__(self, socket, serversocket, remotehost, remoteport):
        self.socket = socket
        self.serversocket = serversocket
        self.remotehost = remotehost
        self.remoteport = remoteport
    
    def __repr__(self):
        return self.remotehost + ":" + str(self.remoteport)
    
    def __str__(self):
        return self.__repr__()
