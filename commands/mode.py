from classes import ModeChange
from numerics import RPL_CHANNELMODEIS, RPL_CREATIONTIME

def run(client, line, serverhandler): # TODO
    changes = []
    to = line.readWord()
    if line.isMoreToRead():
        split = line.readToEnd().split(" ")
        paramindex = 1
        for char in split[0]:
            if char is "+":
                give = True
            elif char is "-":
                give = False
            elif char in ["o", "v", "h", "q", "a"]:
                changes.append(ModeChange(to, client, char, give, split[paramindex]))
                paramindex += 1
            else:
                changes.append(ModeChange(to, client, char, give))
    else: # Just get the mode of the target.
        channel = serverhandler.getChannel(to)
        client.sendNumeric(RPL_CHANNELMODEIS, channel.name, channel.getMode())
        client.sendNumeric(RPL_CREATIONTIME, channel.name, channel.creationTime)