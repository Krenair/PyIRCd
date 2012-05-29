import os
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0, parentdir)
import classes

def run(client, line, serverhandler):
    if not client.loggedIn:
        client.sendNumeric("451", ":You have not registered")
        return

    if 'keys' in line.getFields() and len(line.channels) != len(line.keys):
        pass # TODO: Error properly.

    for index in range(0, len(line.channels)):
        channelName = line.channels[index].name
        if 'keys' in line.getFields():
            key = line.keys[index]
        else:
            key = None

        for existingChannel in serverhandler.channels:
            if existingChannel.name == channelName:
                existingChannel.tryJoin(client, key)
                break

        # This channel doesn't exist already, create it.
        channel = classes.Channel(channelName, client, serverhandler)
        client.tryJoin(channel, None)