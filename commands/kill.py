from numerics import ERR_NOPRIVILEGES, ERR_NOSUCHNICK

def getCommandNames():
    return ['KILL']

def run(client, line, serverhandler):
    targetName = line.readWord()
    comment = line.readWord()[1:]

    target = serverhandler.getClient(targetName)

    if 'o' not in client.modes:
        client.sendNumeric(ERR_NOPRIVILEGES)
    elif target is None:
        client.sendNumeric(ERR_NOSUCHNICK)
    else:
        killMessage = "Killed (" + client.nickname + " (" + comment + "))"
        target.writeLine("ERROR :Closing link: " + target.hostname + " (" + killMessage + ")")
        serverhandler.socketDisconnected(target.socket, killMessage)