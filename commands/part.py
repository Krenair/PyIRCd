from numerics import ERR_NOSUCHCHANNEL, ERR_NOTONCHANNEL

def run(client, line, serverhandler):
    for channel in line.readWord().split(","):
        channel = serverhandler.getChannel(channel)
        if channel is None:
            client.sendNumeric(ERR_NOSUCHCHANNEL, channel.name)
        elif client not in channel.members:
            client.sendNumeric(ERR_NOTONCHANNEL, channel.name)
        else:
            for channelMember in channel.members:
                channelMember.writeLine(":" + str(client) + " PART " + channel.name)
            client.channels.remove(channel)
            channel.memberLeave(client)