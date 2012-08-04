import time
from numerics import *

def getCommandNames():
    return ['WHOIS']

def run(client, line, serverhandler):
    for targetName in line.readWord().split(","):
        target = serverhandler.getClient(targetName)
        if target is None: # No such client.
            client.sendNumeric(ERR_NOSUCHNICK, targetName)
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

            client.sendNumeric(RPL_WHOISIDLE, target.nickname, int(time.time()) - target.lastActiveTime, target.signOnTime)
            client.sendNumeric(RPL_ENDOFWHOIS, target.nickname)
