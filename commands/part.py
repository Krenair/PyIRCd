def run(client, line, serverhandler):
    for channel in line.readWord().split(","):
        channel = serverhandler.getChannel(channel)
        if channel is None:
            client.sendNumeric("403", channel.name + " :No such channel") #ERR_NOSUCHCHANNEL
        elif client not in channel.members:
            client.sendNumeric("442", channel.name + " :You're not on that channel") #ERR_NOTONCHANNEL
        else:
            client.channels.remove(channel)
            channel.members.remove(client)
            for channelMember in channel.members:
                channelMember.writeLine(":" + str(client) + " PART " + channel.name)