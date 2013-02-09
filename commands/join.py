from classes import Channel
from numerics import ERR_NOTREGISTERED

def getCommandNames():
    return ['JOIN']

def run(client, line, serverhandler):
    channels = line.readWord().split(",")
    if line.isMoreToRead():
        keys = line.readWord().split(",")
    else:
        keys = None

    if not client.loggedIn:
        client.sendNumeric(ERR_NOTREGISTERED)
        return

    for index in range(0, len(channels)):
        channelName = channels[index]
        if keys is None:
            key = None
        else:
            key = keys[index]

        channel = serverhandler.getChannel(channelName)
        if channel is None:
            channel = Channel(channelName, client, serverhandler) # This channel doesn't exist already, create it.

        client.tryJoin(channel, key)
