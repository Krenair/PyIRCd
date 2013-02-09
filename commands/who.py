from numerics import RPL_WHOREPLY, RPL_ENDOFWHO

def getCommandNames():
    return ['WHO']

def run(client, line, serverhandler):
    if line.isMoreToRead():
        pattern = line.readWord()

    operatorsOnly = line.isMoreToRead()
    line.readToEnd()

    channel = serverhandler.getChannel(pattern) #TODO: Make this support more than just channels.
    if channel is None:
        return

    for channelMember in channel.members:
        if channelMember.isAway():
            flags = "G"
        else:
            flags = "H"

        if channelMember in channel.userModes['v']:
            flags += '+'

        if channelMember in channel.userModes['h']:
            flags += '%'

        if channelMember in channel.userModes['o']:
            flags += '@'

        if channelMember in channel.userModes['a']:
            flags += '&'

        if channelMember == channel.owner:
            flags += '~'

        client.sendNumeric(RPL_WHOREPLY, channel.name, channelMember.username, channelMember.hostname, serverhandler.config.servername, channelMember.nickname, flags, '0', channelMember.realname)

    client.sendNumeric(RPL_ENDOFWHO, pattern)
