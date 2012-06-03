import os
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0, parentdir)
import classes

def run(client, line, serverhandler):
    channels = line.readWord().split(",")
    if line.isMoreToRead():
        keys = line.readWord().split(",")
    else:
        keys = None

    if not client.loggedIn:
        client.sendNumeric("451", ":You have not registered")
        return

    if keys is not None and len(channels) != len(keys):
        pass # TODO: Error properly.

    for index in range(0, len(channels)):
        channelName = channels[index]
        if 'keys' is None:
            key = None
        else:
            key = keys[index]

        for existingChannel in serverhandler.channels:
            if existingChannel.name == channelName:
                existingChannel.tryJoin(client, key)
                break

        # This channel doesn't exist already, create it.
        channel = classes.Channel(channelName, client, serverhandler)
        client.tryJoin(channel, None)