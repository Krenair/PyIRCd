from numerics import RPL_ENDOFNAMES, RPL_NAMREPLY

def run(client, line, serverhandler):
    for channelName in line.readWord().split(","):
        channel = serverhandler.getChannel(channelName)
        if channel is not None:
            memberInfo = ''
            for channelMember in channel.members:
                if channelMember == channel.owner:
                    memberInfo += '~'
                elif channelMember in channel.userModes['a']:
                    memberInfo += '&'
                elif channelMember in channel.userModes['o']:
                    memberInfo += '@'
                elif channelMember in channel.userModes['h']:
                    memberInfo += '%'
                elif channelMember in channel.userModes['v']:
                    memberInfo += '+'

                memberInfo += channelMember.nickname + ' '

            client.sendNumeric(RPL_NAMREPLY, "= " + channel.name, memberInfo[:-1])
        client.sendNumeric(RPL_ENDOFNAMES, channelName)