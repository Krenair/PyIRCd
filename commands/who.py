def run(client, line, serverhandler):
    channel = serverhandler.getchannel(line.pattern) #TODO: Make this support more than just channels.
    if channel is None:
        return

    for channelMember in channel.members:
        flags = "H" #TODO: Work out why this should be G in some situations.

        if channelMember in channel.userModes['o']:
            flags += '@'

        if channelMember in channel.userModes['v']:
            flags += '+'

        client.sendNumeric("352", channel.name + " " + channelMember.username + " " + channelMember.hostname + " " + serverhandler.config.servername + " " + channelMember.nickname + " " + flags + " :0 " + channelMember.realname[1:])

    client.sendNumeric("315", line.pattern + " :End of /WHO list.")