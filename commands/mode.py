from classes import ModeChange
from numerics import RPL_CHANNELMODEIS, RPL_CREATIONTIME, ERR_NOSUCHCHANNEL, ERR_NOSUCHNICK, RPL_UMODEIS

def getCommandNames():
    return ['MODE']

def run(client, line, serverhandler):
    to = line.readWord()
    if serverhandler.isChannelName(to) and not serverhandler.getChannel(to):
        client.sendNumeric(ERR_NOSUCHCHANNEL, to)
        return
    elif not serverhandler.getClient(to):
        client.sendNumeric(ERR_NOSUCHNICK, to)
        return

    if line.isMoreToRead():
        changes = []
        split = line.readToEnd().split(" ")
        paramindex = 1
        for char in split[0]:
            if char is "+":
                give = True
            elif char is "-":
                give = False
            #elif char in ["o", "v", "h", "q", "a"] and serverhandler.getChannel(to):
                #changes.append(ModeChange(to, client, char, give, split[paramindex]))
                #paramindex += 1
            else:
                changes.append(ModeChange(to, client, char, give))

        if serverhander.isChannelName(to):
            pass
        else:
            print(changes)
            for change in changes:
                if change.give:
                    to.modes.add(change.char)
                else:
                    to.modes.remove(change.char)
            if to == client:
                to.writeLine(":" + serverhandler.config.servername + " MODE " + to.nickname + " :" + split[0])
            else:
                text = ":" + str(client) + " MODE " + to.nickname + " :" + split[0]
                to.writeLine(text)
                client.writeLine(text)
    else: # Just get the mode of the target.
        if serverhandler.isChannelName(to):
            channel = serverhandler.getChannel(to)
            client.sendNumeric(RPL_CHANNELMODEIS, channel.name, channel.getMode())
            client.sendNumeric(RPL_CREATIONTIME, channel.name, channel.creationTime)
        else:
            target = serverhandler.getClient(to)
            client.sendNumeric(RPL_UMODEIS, '+' + ''.join(sorted(target.modes)))
