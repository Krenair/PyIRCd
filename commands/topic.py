def run(client, line, serverhandler):
    channelName = line.readWord()
    if line.isMoreToRead():
        topic = line.readToEnd()[1:]
    else:
        topic = None

    channel = serverhandler.getChannel(channelName)
    if channel is None:
        client.sendNumeric("403", channelName + " :No such channel")
    elif topic is not None:
        if client not in channel.members:
            client.sendNumeric("442", channel.name + " :You're not on that channel")
        elif 't' in channel.modes and client not in channel.userModes['o']:
            client.sendNumeric("482", channel.name + " :You're not a channel operator")
        else:
            channel.topic = topic
            for channelMember in channel.members:
                channelMember.writeLine(":" + str(client) + " TOPIC " + channel.name + " :" + channel.topic)
    elif channel.topic is None:
        client.sendNumeric("331", channel.name + " :No topic is set.")
    else:
        client.sendNumeric("332", channel.name + " :" + channel.topic)
        if channel.topicLastChangedAt is not None: # If it's not been changed before...
            client.sendNumeric("333", channel.name + " " + channel.topicLastChangedBy + " " + channel.topicLastChangedAt)