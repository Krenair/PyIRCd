class LineType:
    Capabilities = "CAP"
    Password = "PASS"
    Nickname = "NICK"
    Username = "USER"
    Server = "SERVER"
    Operator = "OPER"
    Quit = "QUIT"
    ServerQuit = "SQUIT"
    Join = "JOIN"
    Part = "PART"
    Mode = "MODE"
    Topic = "TOPIC"
    Names = "NAMES"
    List = "LIST"
    Invite = "INVITE"
    Kick = "KICK"
    Version = "VERSION"
    Statistics = "STATS"
    Links = "LINKS"
    Time = "TIME"
    Connect = "CONNECT"
    Trace = "TRACE"
    Administrator = "ADMIN"
    Infomation = "INFO"
    Message = "PRIVMSG"
    Notice = "NOTICE"
    Who = "WHO"
    WhoIs = "WHOIS"
    WhoWas = "WHOWAS"
    Kill = "KILL"
    Ping = "PING"
    Pong = "PONG"
    Error = "ERROR"
    Away = "AWAY"
    Rehash = "REHASH"
    Restart = "RESTART"
    Summon = "SUMMON"
    Users = "USERS"
    OperatorsWall = "WALLOPS"
    UserHost = "USERHOST"
    IsOn = "ISON"

class Line:
    def __init__(self, line):
        self.offset = 0
        self.line = line
        firstword = self.readWord()
        if firstword == "CAP":
            self.type = LineType.Capabilities
            self.capabilities = self.readToEnd()
        elif firstword == "PASS":
            self.type = LineType.Password
            self.password = self.readWord()
        elif firstword == "NICK":
            self.type = LineType.Nickname
            self.nickname = self.readWord()
            if self.isMoreToRead():
                self.hopcount = self.readWord()
        elif firstword == "USER":
            self.type = LineType.Username
            self.username = self.readWord()
            self.hostname = self.readWord()
            self.servername = self.readWord()
            self.realname = self.readWord()
        elif firstword == "SERVER":
            self.type = LineType.Server
            self.servername = self.readWord()
            self.hopcount = self.readWord()
            self.info = self.readWord()
        elif firstword == "OPER":
            self.type = LineType.Operator
            self.username = self.readWord()
            self.password = self.readWord()
        elif firstword == "QUIT":
            self.type = LineType.Quit
            if self.isMoreToRead():
                self.quitmessage = self.readWord()
        elif firstword == "SQUIT":
            self.type = LineType.ServerQuit
            self.server = self.readWord()
            self.comment = self.readWord()
        elif firstword == "JOIN":
            self.type = LineType.Join
            self.channels = self.readWord().split(",")
            if self.isMoreToRead():
                self.keys = self.readWord().split(",")
        elif firstword == "PART":
            self.type = LineType.Part
            self.channels = self.readWord().split(",")
        elif firstword == "MODE":
            self.type = LineType.Mode
            self.modes = []
            to = self.readWord()
            data = self.readToEnd()
            split = data.split(" ")
            paramindex = 1
            for mode in split[0]:
                if mode is "+":
                    give = True
                elif mode is "-":
                    give = False
                elif mode in ["o", "v", "h", "q", "a"]:
                    self.modes.append(Mode(to, mode, give, split[paramindex]))
                    paramindex += 1
                else:
                    self.modes.append(Mode(to, mode, give))
        elif firstword == "TOPIC":
            self.type = LineType.Topic
            self.channel = self.readWord()
            if self.isMoreToRead():
                self.topic = self.readWord()
        elif firstword == "NAMES":
            self.type = LineType.Names
            self.channels = self.readWord()
        elif firstword == "LIST":
            self.type = LineType.List
            if self.isMoreToRead():
                self.channels = self.readWord()
                if self.isMoreToRead():
                    self.server = self.readWord()
        elif firstword == "INVITE":
            self.type = LineType.Invite
            self.nickname = self.readWord()
            self.channel = self.readWord()
        elif firstword == "KICK":
            self.type = LineType.Kick
            self.channel = self.readWord()
            self.nickname = self.readWord()
            if self.isMoreToRead():
                self.comment = self.readWord()
        elif firstword == "VERSION":
            self.type = LineType.Version
            if self.isMoreToRead():
                self.server = self.readWord()
        elif firstword == "STATS":
            self.type = LineType.Statistics
            if self.isMoreToRead():
                self.query = self.readWord()
                if self.isMoreToRead():
                    self.server = self.readWord()
        elif firstword == "LINKS":
            self.type = LineType.Links
            if self.isMoreToRead():
                word1 = self.readWord()
                if self.isMoreToRead():
                    self.remoteserver = word1
                    self.servermask = self.readWord()
                else:
                    self.servermask = word1
        elif firstword == "TIME":
            self.type = LineType.Time
            if self.isMoreToRead():
                self.server = self.readWord()
        elif firstword == "CONNECT":
            self.type = LineType.Connect
            self.targetserver = self.readWord()
            if self.isMoreToRead():
                self.port = self.readWord()
                if self.isMoreToRead():
                    self.remoteserver = self.readWord()
        elif firstword == "TRACE":
            self.type = LineType.Trace
            if self.isMoreToRead():
                self.server = self.readWord()
        elif firstword == "ADMIN":
            self.type = LineType.Administrator
            if self.isMoreToRead():
                self.server = self.readWord()
        elif firstword == "INFO":
            self.type = LineType.Information
            if self.isMoreToRead():
                self.server = self.readWord()
        elif firstword == "PRIVMSG":
            self.type = LineType.Message
            self.receivers = self.readWord()
            self.text = self.readToEnd()
        elif firstword == "NOTICE":
            self.type = LineType.Notice
            self.receivers = self.readWord()
            self.text = self.readToEnd()
        elif firstword == "WHO":
            self.type = LineType.Who
            if self.isMoreToRead():
                self.pattern = self.readWord()
                self.operatorsOnly = self.isMoreToRead()
                self.readToEnd()
        elif firstword == "WHOIS":
            self.type = LineType.WhoIs
            word1 = self.readWord()
            if self.isMoreToRead():
                self.server = word1
                self.nickmasks = self.readWord()
            else:
                self.nickmasks = word1
        elif firstword == "WHOWAS":
            self.type = LineType.WhoWas
            self.nickname = self.readWord()
            if self.isMoreToRead():
                self.count = self.readWord()
                if self.isMoreToRead():
                    self.server = self.readWord()
        elif firstword == "KILL":
            self.type = LineType.Kill
            self.nickname = self.readWord()
            self.comment = self.readWord()
        elif firstword == "PING":
            self.type = LineType.Ping
            self.text = self.readWord()
            if self.isMoreToRead():
                self.server = self.readWord()
        elif firstword == "PONG":
            self.type = LineType.Pong
            self.daemon = self.readWord()
            if self.isMoreToRead():
                self.daemon2 = self.readWord()
        elif firstword == "ERROR":
            self.type = LineType.Error
            self.errormessage = self.readWord()
        elif firstword == "AWAY":
            self.type = LineType.Away
            if self.isMoreToRead():
                self.message = self.readWord()
        elif firstword == "REHASH":
            self.type = LineType.Rehash
        elif firstword == "RESTART":
            self.type = LineType.Restart
        elif firstword == "SUMMON":
            self.type = LineType.Summon
            self.user = self.readWord()
            if self.isMoreToRead():
                self.server = self.readWord()
        elif firstword == "USERS":
            self.type = LineType.Users
            if self.isMoreToRead():
                self.server = self.readWord()
        elif firstword == "WALLOPS":
            self.type = LineType.OperatorsWall
            self.message = self.readToEnd()
        elif firstword == "USERHOST":
            self.type = LineType.UserHost
            self.nicknames = self.readToEnd()
        elif firstword == "ISON":
            self.type = LineType.IsOn
            self.nicknames = self.readToEnd()

    def readWord(self):
        #read until the next space
        buffer = ""
        for character in self.line[self.offset:]:
            self.offset += 1
            if character == " " or character == "\r\n":
                return buffer
            else:
                buffer += character
        return buffer

    def readToEnd(self):
        returned = self.line[self.offset:]
        self.offset = len(self.line)
        return returned

    def isMoreToRead(self):
        if len(self.line) == self.offset:
            return False
        return True

    def isChannelName(self, name):
        if name[0] == "#":
            return True
        else:
            return False

    def getFields(self):
        out = []
        ignore = ['__doc__', '__init__', '__module__', 'isChannelName', 'isMoreToRead', 'readToEnd', 'readWord', 'getFields', 'line', 'offset']
        for field in dir(self):
            if field not in ignore:
                out.append(field)
        return out

class Mode:
    def __init__(self, to, mode, given, nick = None):
        self.to = to
        self.mode = mode
        self.given = given
        self.nick = nick
