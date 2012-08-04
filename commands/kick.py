from numerics import *

def getCommandNames():
    return ['KICK']

def run(client, line, serverhandler):
    channelName = line.readWord()
    targetName = line.readWord()

    if line.isMoreToRead():
        comment = line.readToEnd()[1:]
    else:
        comment = targetName

    target = serverhandler.getClient(targetName)
    channel = serverhandler.getChannel(channelName)

    if channel is None:
        client.sendNumeric(ERR_NOSUCHCHANNEL, channelName)
    elif target is None:
        client.sendNumeric(ERR_NOSUCHNICK, targetName)
    elif target not in channel.members:
        client.sendNumeric(ERR_USERNOTINCHANNEL, target.nickname, channel.name)
    elif client not in channel.members:
        client.sendNumeric(ERR_NOTONCHANNEL, channel.name)
    elif client not in channel.getOps():
        client.sendNumeric(ERR_CHANOPRIVSNEEDED, channelName)
    else:
        for channelMember in channel.members:
            channelMember.writeLine(":" + str(client) + " KICK " + channel.name + " " + target.nickname)
        channel.memberLeave(target)
