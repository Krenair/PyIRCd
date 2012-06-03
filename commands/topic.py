def run(client, line, serverhandler):
    channel = line.readWord()
    if line.isMoreToRead():
        topic = line.readWord()
    else:
        topic = None

    channel = serverhandler.getChannel(channel)
    if channel is None:
        client.sendNumeric("403", channel + " :No such channel")
    elif topic is not None:
        if client not in channel.members:
            client.sendNumeric("442", channel + " :You're not on that channel")
        elif 't' in channel.modes and client not in channel.userModes['o']:
            client.sendNumeric("482", channel + " :You're not a channel operator")
        else:
            channel.topic = topic
            for channelMember in channel.members:
                channelMember.writeLine(":" + str(client) + " TOPIC " + channel.name + " :" + channel.topic)
    elif channel.topic is None:
        client.sendNumeric("331", channel + " :No topic is set.")
    else:
        client.sendNumeric("332", channel + " :" + channel.topic)
        client.sendNumeric("333", channel + " " + channel.topicLastChangedBy + " " + channel.topicLastChangedAt)