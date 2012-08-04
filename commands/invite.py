from numerics import *

def getCommandNames():
    return ['INVITE']

def run(client, line, serverhandler):
    targetName = line.readWord()
    channelName = line.readWord()

    target = serverhandler.getClient(targetName)
    if target is None:
        client.sendNumeric(ERR_NOSUCHNICK, targetName)
        return

    channel = serverhandler.getChannel(channelName)
    if channel is not None:
        if client not in channel.members:
            client.sendNumeric(ERR_NOTONCHANNEL, channel.name)
            return
        elif 'i' in channel.modes and client not in channel.getOps():
            client.sendNumeric(ERR_CHANOPRIVSNEEDED, channel.name)
            return
        elif target in channel.members:
            client.sendNumeric(ERR_USERONCHANNEL, targetName, channel.name)
            return

    if target.awayMessage is not None:
        client.sendNumeric(RPL_AWAY, target.awayMessage)

    target.invitedTo.append(channelName)
    target.writeLine(":" + str(client) + " INVITE " + targetName + " :" + channelName)
    client.sendNumeric(RPL_INVITING, channelName, target.nickname)
