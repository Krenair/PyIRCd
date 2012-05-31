def run(client, line, serverhandler):
    channel = serverhandler.getchannel(line.channel)
    if channel is None:
        client.sendNumeric("403", line.channel + " :No such channel")
    elif 'topic' in line:
        if client not in channel.members:
            client.sendNumeric("442", line.channel + " :You're not on that channel")
        elif 't' in channel.modes and client not in channel.userModes['o']:
            client.sendNumeric("482", line.channel + " :You're not a channel operator")
        else:
            channel.topic = line.topic
            for channelMember in channel.members:
                channelMember.writeline(":" + str(client) + " TOPIC " + channel.name + " :" + channel.topic)
    else:
        if channel.topic is None:
            client.sendNumeric("331", line.channel + " :No topic is set.")
        else:
            client.sendNumeric("332", line.channel + " :" + channel.topic)
            client.sendNumeric("333", line.channel + " " + channel.topicLastChangedBy + " " + channel.topicLastChangedAt)