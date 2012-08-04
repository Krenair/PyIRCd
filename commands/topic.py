from numerics import *

def getCommandNames():
    return ['TOPIC']

def run(client, line, serverhandler):
    channelName = line.readWord()
    if line.isMoreToRead():
        topic = line.readToEnd()[1:]
    else:
        topic = None

    channel = serverhandler.getChannel(channelName)
    if channel is None:
        client.sendNumeric(ERR_NOSUCHCHANNEL, channelName)
    elif topic is not None:
        if client not in channel.members:
            client.sendNumeric(ERR_NOTONCHANNEL, channel.name)
        elif 't' in channel.modes and client not in channel.getOps():
            client.sendNumeric(ERR_CHANOPRIVSNEEDED, channel.name)
        else:
            channel.topic = topic
            for channelMember in channel.members:
                channelMember.writeLine(":" + str(client) + " TOPIC " + channel.name + " :" + channel.topic)
    elif channel.topic is None:
        client.sendNumeric(RPL_NOTOPIC, channel.name)
    else:
        client.sendNumeric(RPL_TOPIC, channel.name, channel.topic)
        if channel.topicLastChangedAt is not None: # If it's not been changed before...
            client.sendNumeric(RPL_TOPICWHOTIME, channel.name, channel.topicLastChangedBy, channel.topicLastChangedAt)
