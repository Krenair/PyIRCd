from numerics import ERR_NOSUCHCHANNEL, ERR_NOTONCHANNEL, ERR_CHANOPRIVSNEEDED

def run(client, line, serverhandler):
    channelName = line.readWord()
    targetName = line.readWord()

    if line.isMoreToRead():
        comment = line.readToEnd()[1:]
    else:
        comment = None

    target = serverhandler.getClient(targetName)
    channel = serverhandler.getChannel(channelName)

    if channel is None:
        client.sendNumeric(ERR_NOSUCHCHANNEL, channelName)
    elif target is None or target not in channel.members: # TODO: Error
        pass
    elif client not in channel.members:
        client.sendNumeric(ERR_NOTONCHANNEL, channel.name)
    elif client != channel.owner and client not in channel.userModes['o'] and client not in channel.userModes['h'] and client not in channel.userModes['o']:
        client.sendNumeric(ERR_CHANOPRIVSNEEDED, channelName)
    else:
        pass