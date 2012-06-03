import commands, sys

class Config:
    # TODO: Actually get stuff from a config file.
    def __init__(self, path):
        self.servername = "localhosttest"
        self.path = path
        self.motd = "Just an example MOTD."

class ServerHandler:
    def __init__(self, config):
        self.config = config
        self.serverSockets = []
        self.clients = {} # Socket -> client
        self.remoteSockets = []
        self.readingFromSockets = []
        self.selectList = [sys.stdin]
        self.channels = []
        self.run = True

    def sigint(self, message):
        for socket in self.clients:
            self.clients[socket].writeLine("ERROR :Closing link: " + str(self.clients[socket]) + " (Server shutdown: " + message + ")")
            self.clientDisconnected(socket)
        for serversocket in self.serverSockets:
            serversocket.close()
    
    def acceptConnection(self, serversocket):
        socket, (remotehost, remoteport) = serversocket.accept()
        self.remoteSockets.append(socket)
        client = Client(socket, serversocket, remotehost, remoteport, self)
        self.clients[socket] = client
        self.selectList.append(socket)
        client.writeLine(":" + self.config.servername + " NOTICE * :*** Looking up your hostname...")
        client.writeLine(":" + self.config.servername + " NOTICE * :*** Checking Ident")
        client.writeLine(":" + self.config.servername + " NOTICE * :*** Found your hostname")

    def readLine(self, stream): # Input from a socket or console.
        if stream == sys.stdin: # Console.
            line = sys.stdin.readline()
        else: # A socket.
            try:
                line = ""
                while True:
                    line += stream.recv(1)
                    if len(line) >= 2 and line[-2:] == "\r\n":
                        line = line[:-2]
                        break
            except Exception as e:
                self.clientDisconnected(stream)
                if stream in self.readingFromSockets:
                    self.readingFromSockets.remove(stream)
                return

        if stream in self.readingFromSockets:
            self.readingFromSockets.remove(stream)

        self.processLine(stream, line)
    
    def processLine(self, stream, line):
        if stream in self.clients:
            client = self.clients[stream]
            print "Line from", str(client) + ":", line
            l = Line(line)

            if l.firstWord not in commands.map.keys():
                client.sendNumeric("421", l.firstWord + " :Unknown command")
                return

            commands.map[l.firstWord].run(client, l, self)
        elif stream == sys.stdin:
            print line
    
    def clientDisconnected(self, socket):
        if socket in self.selectList:
            self.selectList.remove(socket)
        if socket in self.remoteSockets:
            self.remoteSockets.remove(socket)
        if socket in self.readingFromSockets:
            self.readingFromSockets.remove(socket)
        if socket in self.clients.values():
            del self.clients[socket]
        socket.close()
    
    def addServerSocket(self, serversocket):
        self.serverSockets.append(serversocket)
        self.selectList.append(serversocket)

    def getChannel(self, name):
        for channel in self.channels:
            if channel.name == name:
                return channel

    def getClient(self, name):
        for client in self.clients.values():
            if client.nickname == name:
                return client

    def isChannelName(self, name):
        """Tries to determine if something is a valid channel name or not."""
        if len(name) == 0:
            return False
        return name[0] == "#"

class Line:
    def __init__(self, line):
        self.offset = 0
        self.line = line
        self.firstWord = self.readWord().upper()
        if self.firstWord == "CAP":
            self.capabilities = self.readToEnd()
        elif self.firstWord == "PASS":
            self.password = self.readWord()
        elif self.firstWord == "SERVER":
            self.servername = self.readWord()
            self.hopcount = self.readWord()
            self.info = self.readWord()
        elif self.firstWord == "OPER":
            self.username = self.readWord()
            self.password = self.readWord()
        elif self.firstWord == "QUIT":
            if self.isMoreToRead():
                self.quitmessage = self.readWord()
        elif self.firstWord == "SQUIT":
            self.server = self.readWord()
            self.comment = self.readWord()
        elif self.firstWord == "NAMES":
            self.channels = self.readWord()
        elif self.firstWord == "LIST":
            if self.isMoreToRead():
                self.channels = self.readWord()
                if self.isMoreToRead():
                    self.server = self.readWord()
        elif self.firstWord == "INVITE":
            self.nickname = self.readWord()
            self.channel = self.readWord()
        elif self.firstWord == "KICK":
            self.channel = self.readWord()
            self.nickname = self.readWord()
            if self.isMoreToRead():
                self.comment = self.readWord()
        elif self.firstWord == "VERSION":
            if self.isMoreToRead():
                self.server = self.readWord()
        elif self.firstWord == "STATS":
            if self.isMoreToRead():
                self.query = self.readWord()
                if self.isMoreToRead():
                    self.server = self.readWord()
        elif self.firstWord == "LINKS":
            if self.isMoreToRead():
                word1 = self.readWord()
                if self.isMoreToRead():
                    self.remoteserver = word1
                    self.servermask = self.readWord()
                else:
                    self.servermask = word1
        elif self.firstWord == "TIME":
            if self.isMoreToRead():
                self.server = self.readWord()
        elif self.firstWord == "CONNECT":
            self.targetserver = self.readWord()
            if self.isMoreToRead():
                self.port = self.readWord()
                if self.isMoreToRead():
                    self.remoteserver = self.readWord()
        elif self.firstWord == "TRACE":
            if self.isMoreToRead():
                self.server = self.readWord()
        elif self.firstWord == "ADMIN":
            if self.isMoreToRead():
                self.server = self.readWord()
        elif self.firstWord == "INFO":
            if self.isMoreToRead():
                self.server = self.readWord()
        elif self.firstWord == "NOTICE":
            self.receivers = self.readWord()
            self.text = self.readToEnd()
        elif self.firstWord == "WHOIS":
            word1 = self.readWord()
            if self.isMoreToRead():
                self.server = word1
                self.nickmasks = self.readWord()
            else:
                self.nickmasks = word1
        elif self.firstWord == "WHOWAS":
            self.nickname = self.readWord()
            if self.isMoreToRead():
                self.count = self.readWord()
                if self.isMoreToRead():
                    self.server = self.readWord()
        elif self.firstWord == "KILL":
            self.nickname = self.readWord()
            self.comment = self.readWord()
        elif self.firstWord == "PONG":
            self.daemon = self.readWord()
            if self.isMoreToRead():
                self.daemon2 = self.readWord()
        elif self.firstWord == "ERROR":
            self.errormessage = self.readWord()
        elif self.firstWord == "AWAY":
            if self.isMoreToRead():
                self.message = self.readWord()
        elif self.firstWord == "SUMMON":
            self.user = self.readWord()
            if self.isMoreToRead():
                self.server = self.readWord()
        elif self.firstWord == "USERS":
            if self.isMoreToRead():
                self.server = self.readWord()
        elif self.firstWord == "WALLOPS":
            self.message = self.readToEnd()
        elif self.firstWord == "USERHOST":
            self.nicknames = self.readToEnd()
        elif self.firstWord == "ISON":
            self.nicknames = self.readToEnd()

    def readWord(self):
        """ Read until the next space."""
        buffer = ""
        for character in self.line[self.offset:]:
            self.offset += 1
            if character == " " or character == "\r\n":
                return buffer
            else:
                buffer += character
        return buffer

    def readToEnd(self):
        """ Read until the end of the buffer."""
        returned = self.line[self.offset:]
        self.offset = len(self.line)
        return returned

    def isMoreToRead(self):
        """Returns False if we're at the end of the string, True otherwise."""
        if len(self.line) == self.offset:
            return False
        return True

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

    def writeLine(self, line):
        self.socket.send(line + "\r\n")
        print "Line to", str(self) + ":", line

    def sendNumeric(self, number, message):
        if self.nickname is not None:
            self.writeLine(":" + self.serverhandler.config.servername + " " + number + " " + self.nickname + " " + message)

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
            client.writeLine(":" + str(self) + " NICK :"+ newname)

        self.nickname = newname

    def tryJoin(self, channel, key):
        if 'i' in channel.modes.keys() and self not in channel.userModes['i']:
            return False
        elif 'k' in channel.modes.keys() and key != channel.modes['k']:
            return False
        else:
            self.channels.append(channel)
            channel.members.append(self)
            memberInfo = ''
            for channelMember in channel.members:
                channelMember.writeLine(":" + str(self) + " JOIN " + channel.name)

                if channelMember in channel.userModes['o']:
                    memberInfo += '@'
                elif channelMember in channel.userModes['v']:
                    memberInfo += '+'

                memberInfo += channelMember.nickname + ' '

            self.sendNumeric("353", "@ " + channel.name + " :" + memberInfo[:-1])
            self.sendNumeric("366", channel.name + " :End of /NAMES list.")
            if channel.topic is not None:
                self.sendNumeric("332", line.channel + " :" + channel.topic)
                self.sendNumeric("333", line.channel + " " + channel.topicLastChangedBy + " " + channel.topicLastChangedAt)

class Channel:
    def __init__(self, name, owner, serverhandler):
        self.name = name
        self.owner = owner
        self.topic = None
        self.topicLastChangedBy = None
        self.topicLastChangedAt = None
        self.modes = {}
        self.userModes = {'v':[], 'h':[], 'o':[owner], 'a':[]}
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

class ModeChange:
    def __init__(self, to, by, mode, given, nick = None):
        self.to = to
        self.by = by
        self.mode = mode
        self.given = given
        self.nick = nick