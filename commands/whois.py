from time import time
from numerics import RPL_WHOISUSER, RPL_WHOISCHANNELS, RPL_WHOISSERVER, RPL_WHOISSECURE, RPL_AWAY, RPL_WHOISOPERATOR, RPL_WHOISIDLE, RPL_ENDOFWHOIS

def run(client, line, serverhandler):
    for target in line.readWord().split(","):
        target = serverhandler.getClient(target)
        if target is None: # No such client.
            pass
        else:
            client.sendNumeric(RPL_WHOISUSER, target.nickname, target.username, serverhandler.config.servername, '*', target.realname)

            if len(target.channels) > 0:
                channels = ""
                for channel in target.channels:
                    if target in channel.userModes['v']:
                        channels += '+'

                    if target in channel.userModes['h']:
                        channels += '%'

                    if target in channel.userModes['o']:
                        channels += '@'

                    if target in channel.userModes['a']:
                        channels += '&'

                    if target == channel.owner:
                        channels += '~'

                    channels += channel.name + " "

                client.sendNumeric(RPL_WHOISCHANNELS, target.nickname, channels[:-1]) # Channels

            client.sendNumeric(RPL_WHOISSERVER, target.nickname, serverhandler.config.servername, serverhandler.config.serverinfo)

            if target.securelyConnected:
                client.sendNumeric(RPL_WHOISSECURE, target.nickname)

            if target.awayMessage is not None:
                client.sendNumeric(RPL_AWAY, target.nickname, target.awayMessage)

            if 'o' in target.modes:
                client.sendNumeric(RPL_WHOISOPERATOR, target.nickname)

            client.sendNumeric(RPL_WHOISIDLE, target.nickname, int(time()) - target.lastActiveTime, target.signOnTime)
            client.sendNumeric(RPL_ENDOFWHOIS, target.nickname)