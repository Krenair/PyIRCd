from commands import loadCommands
from json import load as json_load
from os import popen, path as os_path
from sys import platform, stdin
from threading import Lock
from time import time, localtime, strftime
from numerics import ERR_UNKNOWNCOMMAND, RPL_TOPICWHOTIME, RPL_MOTDSTART, RPL_MOTD, RPL_ENDOFMOTD, RPL_NAMREPLY, RPL_ENDOFNAMES, RPL_TOPIC, ERR_INVITEONLYCHAN, ERR_BADCHANNELKEY, RPL_LUSERCLIENT, RPL_LUSEROP, RPL_LUSERCHANNELS, RPL_LUSERME, RPL_WELCOME, RPL_YOURHOST, RPL_CREATED, RPL_MYINFO, RPL_ISUPPORT, RPL_LOCALUSERS, RPL_GLOBALUSERS

class Config:
    def __init__(self, path):
        self.path = path
        config = json_load(open(path))
        self.servername = config['servername']
        self.networkname = config['networkname']
        self.port = config['port']
        self.maxclients = config['maxclients']
        self.serverinfo = config['serverinfo']
        self.motd = open(config['motdfile']).read()
        self.opers = config['opers']
        self.operhosts = config['operhosts']
        self.location = config['location']
        self.locationspecific = config['locationspecific']
        self.adminemail = config['adminemail']

class ServerHandler:
    def __init__(self, config):
        self.commandMap = loadCommands()
        self.commandUsage = {}
        for command in self.commandMap.keys():
            self.commandUsage[command] = 0

        self.config = config
        self.serverSockets = []
        self.clients = {} # Socket -> client
        self.remoteSockets = []
        self.readingFromSockets = []
        self.selectList = []
        if platform != 'win32':
            self.selectList.append(stdin)
        self.channels = []
        self.run = True
        self.outputLock = Lock()
        self.creationTime = localtime(os_path.getctime(self.config.path))
        self.startTime = localtime()
        p = popen('git log -n 1 --pretty=format:"%h"')
        self.version = 'git/' + p.read()
        p.close()
        self.connectionsReceived = 0
        self.highestConnectionCount = 0

    def sigint(self, message):
        for socket, client in dict(self.clients).items():
            client.writeLine("ERROR :Closing link: " + self.clients[socket].hostname + " (Server shutdown: " + message + ")")
            self.socketDisconnected(socket, "Server shutdown: " + message)

        for serversocket in self.serverSockets:
            serversocket.close()
    
    def acceptConnection(self, serversocket):
        socket, (remotehost, remoteport) = serversocket.accept()
        self.remoteSockets.append(socket)
        client = Client(socket, serversocket, remotehost, remoteport, self)
        self.clients[socket] = client
        self.selectList.append(socket)
        self.connectionsReceived += 1
        if self.connectionsReceived > self.highestConnectionCount:
            self.highestConnectionCount = self.connectionsReceived

        client.writeLine(":" + self.config.servername + " NOTICE * :*** Looking up your hostname...")
        client.writeLine(":" + self.config.servername + " NOTICE * :*** Checking Ident")
        client.writeLine(":" + self.config.servername + " NOTICE * :*** Found your hostname")

    def readLine(self, stream): # Input from a socket or console.
        if stream == stdin: # Console.
            line = stdin.readline()
        else: # A socket.
            try:
                line = ""
                while True:
                    line += stream.recv(1)
                    if len(line) >= 2 and line[-2:] == "\r\n":
                        line = line[:-2]
                        break
            except Exception as e:
                self.socketDisconnected(stream, "Read error")
                return

            if stream in self.readingFromSockets:
                self.readingFromSockets.remove(stream)

        self.processLine(stream, line)
    
    def processLine(self, stream, line):
        if stream in self.clients:
            client = self.clients[stream]
            self.outputLock.acquire()
            print "Line from", str(client) + ":", line
            self.outputLock.release()
            l = Line(line)

            if l.firstWord not in ['PING', 'PONG']:
                client.lastActiveTime = int(time())

            if l.firstWord not in self.commandMap.keys():
                client.sendNumeric(ERR_UNKNOWNCOMMAND, l.firstWord)
                return

            self.commandUsage[l.firstWord] += 1

            self.commandMap[l.firstWord].run(client, l, self)
        elif stream == stdin:
            print line
    
    def socketDisconnected(self, socket, message = None):
        if socket in self.clients.keys():
            client = self.clients[socket]
            clientsToNotify = []
            for channel in client.channels:
                for member in channel.members:
                    if member not in clientsToNotify and member != client:
                        clientsToNotify.append(member)
                channel.memberLeave(client)

            for clientToNotify in clientsToNotify:
                clientToNotify.writeLine(":" + str(client) + " QUIT :" + message)

        if socket in self.selectList:
            self.selectList.remove(socket)
        if socket in self.remoteSockets:
            self.remoteSockets.remove(socket)
        if socket in self.readingFromSockets:
            self.readingFromSockets.remove(socket)
        if socket in self.clients.keys():
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
        if len(name) < 1:
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
        elif self.firstWord == "SQUIT":
            self.server = self.readWord()
            self.comment = self.readWord()
        elif self.firstWord == "LIST":
            if self.isMoreToRead():
                self.channels = self.readWord()
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
        elif self.firstWord == "CONNECT":
            self.targetserver = self.readWord()
            if self.isMoreToRead():
                self.port = self.readWord()
                if self.isMoreToRead():
                    self.remoteserver = self.readWord()
        elif self.firstWord == "TRACE":
            if self.isMoreToRead():
                self.server = self.readWord()
        elif self.firstWord == "WHOWAS":
            self.nickname = self.readWord()
            if self.isMoreToRead():
                self.count = self.readWord()
                if self.isMoreToRead():
                    self.server = self.readWord()
        elif self.firstWord == "PONG":
            self.daemon = self.readWord()
            if self.isMoreToRead():
                self.daemon2 = self.readWord()
        elif self.firstWord == "ERROR":
            self.errormessage = self.readWord()
        elif self.firstWord == "SUMMON":
            self.user = self.readWord()
            if self.isMoreToRead():
                self.server = self.readWord()
        elif self.firstWord == "USERS":
            if self.isMoreToRead():
                self.server = self.readWord()
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
        self.modes = []
        self.invitedTo = [] # A list of channel names this user has been invited to.
        self.signOnTime = int(time())
        self.lastActiveTime = int(time())
        self.awayMessage = None
        self.securelyConnected = False
    
    def __repr__(self):
        return self.remotehost + ":" + str(self.remoteport)
    
    def __str__(self):
        if self.nickname is None or self.username is None:
            return repr(self)

        return self.nickname + "!" + self.username + "@" + self.remotehost

    def writeLine(self, line):
        self.socket.send(line + "\r\n")
        self.serverhandler.outputLock.acquire()
        print "Line to", str(self) + ":", line
        self.serverhandler.outputLock.release()

    def sendNumeric(self, (number, format), *args):
        if self.loggedIn:
            self.writeLine(":" + self.serverhandler.config.servername + " " + number + " " + self.nickname + " " + (format % args))

    def login(self):
        self.loggedIn = True
        self.sendNumeric(RPL_WELCOME, self.serverhandler.config.networkname, self.nickname)
        self.sendNumeric(RPL_YOURHOST, self.serverhandler.config.servername, self.serverhandler.config.servername, self.serverhandler.config.port, self.serverhandler.version)
        self.sendNumeric(RPL_CREATED, strftime('on %a %-e %b %G at %H:%M:%S %Z', self.serverhandler.creationTime))
        self.sendNumeric(RPL_MYINFO, self.serverhandler.config.servername, self.serverhandler.version)
        self.sendSupports()
        clientcount = len(self.serverhandler.clients)
        self.sendNumeric(RPL_LUSERCLIENT, clientcount, 0, 1) # 0 invisible users, 1 server

        opers = 0
        for client in self.serverhandler.clients.values():
            if 'o' in client.modes:
                opers += 1

        self.sendNumeric(RPL_LUSEROP, opers)
        self.sendNumeric(RPL_LUSERCHANNELS, len(self.serverhandler.channels))
        self.sendNumeric(RPL_LUSERME, len(self.serverhandler.clients), 1) # 1 server
        maxclients = self.serverhandler.config.maxclients
        self.sendNumeric(RPL_LOCALUSERS, clientcount, maxclients, clientcount, maxclients) #RPL_LOCALUSERS
        self.sendNumeric(RPL_GLOBALUSERS, clientcount, maxclients, clientcount, maxclients) #RPL_GLOBALUSERS
        self.sendMOTD()

    def sendSupports(self): # TODO
        self.sendNumeric(RPL_ISUPPORT, "CHANTYPES=# CASEMAPPING=ascii CHANMODES=,,,it PREFIX=(qaohv)~&@%+ NETWORK=" + self.serverhandler.config.networkname) #http://www.irc.org/tech_docs/005.html

    def sendMOTD(self):
        self.sendNumeric(RPL_MOTDSTART, self.serverhandler.config.servername)
        for line in self.serverhandler.config.motd.splitlines():
            self.sendNumeric(RPL_MOTD, line)
        self.sendNumeric(RPL_ENDOFMOTD)

    def setNickname(self, newname):
        if self.loggedIn:
            clientsToBeNotified = [self]

            for channel in self.channels:
                for member in channel.members:
                    if member not in clientsToBeNotified:
                        clientsToBeNotified.append(member)

            for client in clientsToBeNotified:
                client.writeLine(":" + str(self) + " NICK :"+ newname)

        self.nickname = newname

    def tryJoin(self, channel, key):
        if 'i' in channel.modes and channel.name not in self.invitedTo:
            self.sendNumeric(ERR_INVITEONLYCHAN, channel.name)
        elif 'k' in channel.modes and key != channel.modes['k']:
            self.sendNumeric(ERR_BADCHANNELKEY, channel.name)
        else:
            if channel.name in self.invitedTo:
                self.invitedTo.remove(channel.name)

            self.channels.append(channel)
            channel.members.append(self)
            memberInfo = ''
            for channelMember in channel.members:
                channelMember.writeLine(":" + str(self) + " JOIN " + channel.name)

                if channelMember == channel.owner:
                    memberInfo += '~'
                elif channelMember in channel.userModes['a']:
                    memberInfo += '&'
                elif channelMember in channel.userModes['o']:
                    memberInfo += '@'
                elif channelMember in channel.userModes['h']:
                    memberInfo += '%'
                elif channelMember in channel.userModes['v']:
                    memberInfo += '+'

                memberInfo += channelMember.nickname + ' '

            self.sendNumeric(RPL_NAMREPLY, "= " + channel.name, memberInfo[:-1])
            self.sendNumeric(RPL_ENDOFNAMES, channel.name)
            if channel.topic is not None:
                self.sendNumeric(RPL_TOPIC, channel, channel.topic)
                if channel.topicLastChangedAt is not None: # If it's not been changed before...
                    self.sendNumeric(RPL_TOPICWHOTIME, channel.name, channel.topicLastChangedBy, channel.topicLastChangedAt)

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
        self.creationTime = int(time())
        serverhandler.channels.append(self)

    def getMode(self):
        out = ''
        for key, value in self.modes:
            out += '+' + key + ' '

        for key, value in self.modes:
            if value is not None:
                out += value + ' '
        return out[:-1]

    def memberLeave(self, member):
        self.members.remove(member)
        member.channels.remove(self)
        for modeGroup in self.userModes.values():
            if member in modeGroup:
                modeGroup.remove(member)

        if len(self.members) < 1:
            self.serverhandler.channels.remove(self)

    def getOps(self):
        return list(set([self.owner] + self.userModes['a'] + self.userModes['o'] + self.userModes['h']))

class ModeChange:
    def __init__(self, to, by, mode, given, nick = None):
        self.to = to
        self.by = by
        self.mode = mode
        self.given = given
        self.nick = nick
