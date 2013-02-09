import commands, imp, json, os, pkgutil, sys, time
from numerics import *
from threading import Lock

class Config:
    def __init__(self, path):
        config = json.load(open(path))
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
    def __init__(self, configPath):
        self.loadCommands()
        self.commandUsage = {}
        for command in list(self.commandMap.keys()):
            self.commandUsage[command] = 0

        self.config = Config(configPath)
        self.configPath = configPath
        self.serverSockets = []
        self.clients = {} # Socket -> client
        self.remoteSockets = []
        self.readingFromSockets = []
        self.selectList = []
        if sys.platform != 'win32':
            self.selectList.append(sys.stdin)
        self.channels = []
        self.run = True
        self.outputLock = Lock()
        self.creationTime = time.localtime(os.path.getctime(self.configPath))
        self.startTime = time.localtime()
        p = os.popen('git log -n 1 --pretty=format:"%h"')
        self.version = 'git/' + p.read()
        p.close()
        self.connectionsReceived = 0
        self.highestConnectionCount = 0

    def loadCommands(self):
        self.commandMap = {}
        if 'pyinotify' in sys.modules:
            self.moduleWatcher = ModuleWatcher(self)

        for importer, package_name, _ in pkgutil.iter_modules(["commands"]):
            modInfo = importer.find_module(package_name)
            try:
                module = modInfo.load_module(package_name)
            except ImportError as e:
                print('Failed to load', modInfo.filename)
                continue

            if 'pyinotify' in sys.modules:
                self.moduleWatcher.watch_module("commands/" + package_name)

            for command in module.getCommandNames():
                self.commandMap[command] = module

    def shutdown(self, message):
        if 'pyinotify' in sys.modules and self.moduleWatcher is not None and self.moduleWatcher.notifier.isAlive():
            self.moduleWatcher.stop_watching()

        for socket, client in list(dict(self.clients).items()):
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
        if stream == sys.stdin: # Console.
            line = sys.stdin.readline()
        else: # A socket.
            try:
                line = ""
                while True:
                    line += stream.recv(1).decode('UTF-8')
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
            print("Line from " + str(client) + ": " + line)
            self.outputLock.release()
            l = Line(line)

            if l.firstWord not in ['PING', 'PONG']:
                client.lastActiveTime = int(time.time())

            if l.firstWord not in list(self.commandMap.keys()):
                client.sendNumeric(ERR_UNKNOWNCOMMAND, l.firstWord)
                return

            self.commandUsage[l.firstWord] += 1

            self.commandMap[l.firstWord].run(client, l, self)
        elif stream == sys.stdin:
            print(line)
    
    def socketDisconnected(self, socket, message = None):
        if socket in list(self.clients.keys()):
            client = self.clients[socket]
            if message is not None:
                print(str(client) + " disconnected: " + message)
            else:
                print(str(client) + " disconnected")
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
        if socket in list(self.clients.keys()):
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
        for client in list(self.clients.values()):
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
        elif self.firstWord == "USERS":
            if self.isMoreToRead():
                self.server = self.readWord()

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
        self.signOnTime = int(time.time())
        self.lastActiveTime = int(time.time())
        self.awayMessage = None
        self.securelyConnected = False
    
    def __repr__(self):
        return self.remotehost + ":" + str(self.remoteport)
    
    def __str__(self):
        if self.nickname is None or self.username is None:
            return repr(self)

        return self.nickname + "!" + self.username + "@" + self.remotehost

    def writeLine(self, line):
        if sys.version_info.major == 3:
            self.socket.send(bytes(line + '\r\n', 'UTF-8'))
        else:
            self.socket.send(line + '\r\n')

        self.serverhandler.outputLock.acquire()
        print("Line to " + str(self) + ": " + line)
        self.serverhandler.outputLock.release()

    def sendNumeric(self, numeric, *args):
        if self.loggedIn:
            nickname = self.nickname
        else:
            nickname = '*'

        number, format = numeric
        self.writeLine(":" + self.serverhandler.config.servername + " " + number + " " + nickname + " " + (format % args))

    def login(self):
        self.loggedIn = True
        self.sendNumeric(RPL_WELCOME, self.serverhandler.config.networkname, self.nickname)
        self.sendNumeric(RPL_YOURHOST, self.serverhandler.config.servername, self.serverhandler.config.servername, self.serverhandler.config.port, self.serverhandler.version)
        self.sendNumeric(RPL_CREATED, time.strftime('on %a %-e %b %G at %H:%M:%S %Z', self.serverhandler.creationTime))
        self.sendNumeric(RPL_MYINFO, self.serverhandler.config.servername, self.serverhandler.version)
        self.sendSupports()
        clientcount = len(self.serverhandler.clients)
        self.sendNumeric(RPL_LUSERCLIENT, clientcount, 0, 1) # 0 invisible users, 1 server

        opers = 0
        for client in list(self.serverhandler.clients.values()):
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

    def tryJoin(self, channel, key): # TODO: Add support for +l and +b channel modes
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

    def isAway(self):
        return self.awayMessage != None

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
        self.creationTime = int(time.time())
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
        for modeGroup in list(self.userModes.values()):
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

# The following class is based on https://gist.github.com/1013122
# Watch for any changes in a module or package, and reload it automatically

try:
    from pyinotify import ThreadedNotifier, EventsCodes, WatchManager, ProcessEvent
    class ModuleWatcher(ProcessEvent):
        """Automatically reload any modules or packages as they change"""

        def __init__(self, serverhandler):
            self.wm = WatchManager()
            self.notifier = ThreadedNotifier(self.wm, self)
            self.moduleMap = {}
            self.watchDescriptorMap = {}
            self.serverhandler = serverhandler
            self.shuttingDown = False

            flags = EventsCodes.ALL_FLAGS
            path, watchDescriptor = list(self.wm.add_watch('commands/', flags['IN_CREATE'] | flags['IN_DELETE']).items())[0]
            self.watchDescriptorMap[path] = watchDescriptor

        def _watch_file(self, file_name, modulepath, module):
            """Add a watch for a specific file, and map said file to a module name"""

            file_name = os.path.realpath(file_name)
            self.moduleMap[file_name] = modulepath, module
            flags = EventsCodes.ALL_FLAGS

            a = self.wm.add_watch(file_name, flags['IN_MODIFY'])
            if a == {}:
                return
            path, watchDescriptor = list(a.items())[0]
            self.watchDescriptorMap[path] = watchDescriptor

        def watch_module(self, name):
            """Load a module, determine which files it uses, and watch them"""

            if imp.is_builtin(name) in [-1, 1]:
                # Pretty pointless to watch built-in modules
                return

            f, pathname, description = imp.find_module(name)

            try:
                mod = imp.load_module(name, f, pathname, description)
                if f:
                    self._watch_file(f.name, name, mod)
                else:
                    for root, dirs, files in os.walk(pathname):
                        for filename in files:
                            fpath = os.path.join(root, filename)
                            if fpath.endswith('.py'):
                                self._watch_file(fpath, name, mod)
            finally:
                if f:
                    f.close()

        def start_watching(self):
            """Start the pyinotify watch thread"""
            if self.notifier is not None:
                self.notifier.start()

        def stop_watching(self):
            """Stop the pyinotify watch thread"""
            self.shuttingDown = True

            if self.notifier is not None:
                self.notifier.stop()

        def process_default(self, event):
            if event.maskname == 'IN_IGNORED': # TODO: Watch IN_IGNORED properly.
                self.process_IN_IGNORED(event)
            else:
                print(event)

        def process_IN_CREATE(self, event):
            """A file has been created."""
            if event.name.endswith('.py'):
                self.watch_module('commands/' + event.name[:-3])
                modpath, modname = self.moduleMap[event.pathname]
                f, pathname, description = imp.find_module(modpath)
                try:
                    module = imp.load_module(modpath, f, pathname, description)
                    print('Loaded ' + event.pathname + ' which provides the following command(s): ' + ', '.join(module.getCommandNames()))
                    for command in module.getCommandNames():
                        self.serverhandler.commandMap[command] = module
                finally:
                    if f:
                        f.close()

        def process_IN_DELETE(self, event):
            """A file has been deleted."""
            if (event.name.endswith('.py') or event.name.endswith('.pyc')) and event.pathname in self.moduleMap:
                commands = self.moduleMap[event.pathname][1].getCommandNames()
                print('Unloaded ' + event.name + ' which provided the following command(s): ' + ', '.join(commands))
                del self.watchDescriptorMap[event.pathname]
                for command in commands:
                    del self.serverhandler.commandMap[command]
                del self.moduleMap[event.pathname]

        def process_IN_IGNORED(self, event):
            if not os.path.exists(event.path):
                return
            elif not self.shuttingDown:
                if event.path.endswith('.py'):
                    modname = os.path.relpath(event.path)[:-3]
                elif event.path.endswith('.pyc'):
                    modname = os.path.relpath(event.path)[:-4]
                else:
                    return

                try:
                    imp.find_module(modname)
                except ImportError as ie:
                    print('While trying to load ' + modname + ', received this error: ' + ie)
                    return

                self.process_IN_MODIFY(event)
                del self.watchDescriptorMap[event.path]
                del self.moduleMap[event.path]
                self.watch_module(modname)

        def process_IN_MODIFY(self, event):
            """A file has been changed"""

            modpath, modname = self.moduleMap[event.path]
            f, pathname, description = imp.find_module(modpath)
            try:
                module = imp.load_module(modpath, f, pathname, description)
                print('Reloaded ' + event.path + ' which provides the following command(s): ' + ', '.join(module.getCommandNames()))
                for command in module.getCommandNames():
                    self.serverhandler.commandMap[command] = module
            finally:
                if f:
                    f.close()
except ImportError as e:
    if str(e) == 'No module named pyinotify':
        print('No Pyinotify!')
