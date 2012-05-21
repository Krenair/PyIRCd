import parser, sys

class Config:
    def __init__(self, path):
        self.servername = "localhosttest"
        self.path = path
        self.motd = "Just an example MOTD."

class ServerHandler:
    def __init__(self, config):
        self.config = config
        self.serversockets = []
        self.clients = {} #socket -> client
        self.remotesockets = []
        self.readingfromsockets = []
        self.selectlist = [sys.stdin]
        self.channels = []
        self.run = True

    def sigint(self, message):
        for socket in self.clients:
            self.clients[socket].writeline("ERROR :Closing link: " + str(self.clients[socket]) + " (Server shutdown: " + message + ")")
            self.clientdisconnected(socket)
        for serversocket in self.serversockets:
            serversocket.close()
    
    def acceptconnection(self, serversocket):
        socket, (remotehost, remoteport) = serversocket.accept()
        self.remotesockets.append(socket)
        client = Client(socket, serversocket, remotehost, remoteport, self)
        self.clients[socket] = client
        self.selectlist.append(socket)
        client.writeline(":" + self.config.servername + " NOTICE * :*** Looking up your hostname...")
        client.writeline(":" + self.config.servername + " NOTICE * :*** Checking Ident")
        client.writeline(":" + self.config.servername + " NOTICE * :*** Found your hostname")
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
            print "Line from", str(client) + ":", line
            l = parser.Line(line)
            if 'type' not in dir(l):
                client.sendNumeric("421", line.split(' ')[0] + " :Unknown command")
                return

            if client.loggedIn:
                if l.type == parser.LineType.Nickname:
                    client.nickname = l.nickname
                elif l.type == parser.LineType.Username:
                    client.sendNumeric("462", ":You may not reregister")
                elif l.type == parser.LineType.Join:
                    client.sendNumeric("451", ":You have not registered")
            else:
                if l.type == parser.LineType.Nickname:
                    client.nickname = l.nickname
                    if client.username != None:
                        client.login()
                elif l.type == parser.LineType.Username:
                    client.username = l.username
                    client.realname = l.realname
                    if client.nickname != None:
                        client.login()
                elif l.type == parser.LineType.Join:
                    if 'keys' in l.getFields() and len(l.channels) != len(l.keys):
                        pass # TODO: Error properly.

                    for index in range(0, len(l.channels)):
                        channelName = l.channels[index].name
                        if 'keys' in l.getFields():
                            key = l.keys[index]
                        else:
                            key = None

                        for existingChannel in self.channels:
                            if existingChannel.name == channelName:
                                existingChannel.tryJoin(client, key)
                                break

                        # This channel doesn't exist already, create it.
                        channel = Channel(channel, channelName, client, self)
                        client.tryJoin(channel, None)

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
    def __init__(self, socket, serversocket, remotehost, remoteport, serverhandler):
        self.socket = socket
        self.serversocket = serversocket
        self.remotehost = remotehost
        self.remoteport = remoteport
        self.serverhandler = serverhandler
        self.nickname = None
        self.username = None
        self.hostname = remotehost
        self.realname = None
        self.loggedIn = False
    
    def __repr__(self):
        return self.remotehost + ":" + str(self.remoteport)
    
    def __str__(self):
        return self.__repr__()

    def writeline(self, line):
        self.socket.send(line + "\r\n")
        print "Line to", str(self) + ":", line

    def sendNumeric(self, number, message):
        self.writeline(":" + self.serverhandler.config.servername + " " + number + " " + self.nickname + " " + message)

    def login(self):
        self.loggedIn = True
        self.sendMOTD()

    def sendMOTD(self):
        self.sendNumeric("375", ":- " + self.serverhandler.config.servername + " Message of the Day - ")
        for line in self.serverhandler.config.motd.splitlines():
            self.sendNumeric("372", ":- " + line)
        self.sendNumeric("376", ":End of /MOTD command.")

    def tryJoin(self, channel, key):
        if 'i' in channel.modes.keys() and self not in channel.userModes['i']:
            return False
        elif 'k' in channel.modes.keys() and key != channel.modes['k']:
            return False
        else:
            channel.members.append(self)
            for channelMember in channel.members:
                channelMember.writeline(":" + str(self) + " JOIN " + channel.name)

class Channel:
    def __init__(self, name, owner, serverhandler):
        self.name = name
        self.owner = owner
        self.topic = ''
        self.modes = {}
        self.userModes = {}
        self.members = []
        self.serverhandler = serverhandler
        serverhandler.channels.append(self)

    def getMode(self):
        out = ''
        for key, value in self.modes:
            out += '+' + key + ' '

        for key, value in self.modes:
            if value != None:
                out += value + ' '
        return out[:-1]
