import commands, parser, sys

class Config:
    #TODO: Actually get stuff from a config file.
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
    
    def readline(self, stream): # Input from a socket or console.
        if stream == sys.stdin: # Console.
            line = sys.stdin.readline()
        else: # A socket.
            self.readingfromsockets.append(stream)
            try:
                line = ""
                while True:
                    line += stream.recv(1)
                    if len(line) >= 2 and line[-2:] == "\r\n":
                        line = line[:-2]
                        break
            except Exception as e:
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

            if l.type == parser.LineType.Nickname:
                commands.nick.run(client, l, self)
            elif l.type == parser.LineType.Username:
                commands.user.run(client, l, self)
            elif l.type == parser.LineType.Join:
                commands.join.run(client, l, self)
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
        self.channels = []
    
    def __repr__(self):
        return self.remotehost + ":" + str(self.remoteport)
    
    def __str__(self):
        if self.nickname is None or self.username is None:
            return repr(self)

        return self.nickname + "!" + self.username + "@" + self.remotehost

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

    def setNickname(self, newname):
        clientsToBeNotified = [self]

        for channel in self.channels:
            for member in channel.members:
                if member not in clientsToBeNotified:
                    clientsToBeNotified.append(member)

        for client in clientsToBeNotified:
            client.writeline(":" + str(self) + " NICK :"+ newname)

        self.nickname = newname

    def tryJoin(self, channel, key):
        if 'i' in channel.modes.keys() and self not in channel.userModes['i']:
            return False
        elif 'k' in channel.modes.keys() and key != channel.modes['k']:
            return False
        else:
            self.channels.append(channel)
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
            if value is not None:
                out += value + ' '
        return out[:-1]
