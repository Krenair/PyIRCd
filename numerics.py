# The source for most of these names is RFC 1459, but some come from https://www.alien.net.au/irc/irc2numerics.html

RPL_WELCOME = "001", ":Welcome to the %s, %s"
RPL_YOURHOST = "002", ":Your host is %s[%s/%i], running PyIRCd-%s"
RPL_CREATED = "003", ":This server was created %s"
RPL_MYINFO = "004", "%s PyIRCd-%s"
RPL_ISUPPORT = "005", "%s :are supported by this server"
RPL_STATSCOMMANDS = "212", "%s %i"
RPL_ENDOFSTATS = "219", "%s :End of /STATS report"
RPL_STATSLLINE = "241", "L %s * %s %s"
RPL_STATSUPTIME = "242", ":Server Up %s"
RPL_STATSOLINE = "243", "O %s * %s"
RPL_STATSCONN = "250", ":Highest connection count: %i (%i clients) (%i connections received)"
RPL_LUSERCLIENT = "251", ":There are %i users and %i invisible on %i server(s)"
RPL_LUSEROP = "252", "%i :IRC Operators online"
RPL_LUSERCHANNELS = "254", "%i :channels formed"
RPL_LUSERME = "255", ":I have %i clients and %i server(s)"
RPL_ADMINME = "256", ":Administrative info about %s"
RPL_ADMINLOC1 = "257", ":%s"
RPL_ADMINLOC2 = "258", ":%s"
RPL_ADMINEMAIL = "259", ":%s"
RPL_LOCALUSERS = "265", "%i %i :Current local users %i, max %i"
RPL_GLOBALUSERS = "266", "%i %i :Current global users %i, max %i"
RPL_AWAY = "301", "%s :%s"
RPL_USERHOST = "302", ":%s"
RPL_ISON = "303", ":%s"
RPL_UNAWAY = "305", ":You are no longer marked as being away"
RPL_NOWAWAY = "306", ":You have been marked as being away"
RPL_WHOISUSER = "311", "%s %s %s %s :%s"
RPL_WHOISSERVER = "312", "%s %s :%s"
RPL_WHOISOPERATOR = "313", "%s :is an IRC operator"
RPL_ENDOFWHO = "315", "%s :End of /WHO list"
RPL_WHOISIDLE = "317", "%s %i %i :seconds idle, signon time"
RPL_ENDOFWHOIS = "318", "%s :End of /WHOIS list"
RPL_WHOISCHANNELS = "319", "%s :%s"
RPL_CHANNELMODEIS = "324", "%s %s"
RPL_CREATIONTIME = "329", "%s %i"
RPL_NOTOPIC = "331", "%s :No topic is set"
RPL_TOPIC = "332", "%s :%s"
RPL_TOPICWHOTIME = "333", "%s %s %s"
RPL_INVITING = "341", "%s %s"
RPL_VERSION = "351", "%s.%s %s :%s"
RPL_WHOREPLY = "352", "%s %s %s %s %s %s :%s %s"
RPL_NAMREPLY = "353", "%s :%s"
RPL_ENDOFNAMES = "366", "%s :End of /NAMES list"
RPL_INFO = "371", ":%s"
RPL_MOTD = "372", ":- %s"
RPL_ENDOFINFO = "374", ":End of /INFO list"
RPL_MOTDSTART = "375", ":- %s Message of the day - "
RPL_ENDOFMOTD = "376", ":End of /MOTD command"
RPL_YOUREOPER = "381", ":You are now an IRC operator"
RPL_TIME = "391", "%s :%s"
ERR_NOSUCHNICK = "401", "%s :No such nick/channel"
ERR_NOSUCHCHANNEL = "403", "%s :No such channel"
ERR_CANNOTSENDTOCHAN = "404", "%s :Cannot send to channel"
ERR_UNKNOWNCOMMAND = "421", "%s :Unknown command"
ERR_NICKNAMEINUSE = "433", "%s :Nickname is already in use."
ERR_USERNOTINCHANNEL = "441", "%s %s :They aren't on that channel"
ERR_NOTONCHANNEL = "442", "%s :You're not on that channel"
ERR_USERONCHANNEL = "443", "%s %s :is already on channel"
ERR_NOTREGISTERED = "451", ":You have not registered"
ERR_NEEDMOREPARAMS = "461", "%s :Not enough parameters"
ERR_ALREADYREGISTRED = "462", ":You may not reregister"
ERR_PASSWDMISMATCH = "464", ":Password incorrect"
ERR_INVITEONLYCHAN = "473", "%s :Cannot join channel (+i)"
ERR_BADCHANNELKEY = "475", "%s :Cannot join channel (+k)"
ERR_NOPRIVILEGES = "481", ":Permission Denied- You're not an IRC operator"
ERR_CHANOPRIVSNEEDED = "482", "%s :You're not channel operator"
ERR_NOOPERHOST = "491", ":No O-lines for your host"
RPL_WHOISSECURE = "671", "%s :is using a secure connection"
