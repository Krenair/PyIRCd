from numerics import ERR_ALREADYREGISTRED

def getCommandNames():
    return ['USER']

def run(client, line, serverhandler):
    username = line.readWord()
    hostname = line.readWord()
    servername = line.readWord()
    realname = line.readWord()[1:]

    if client.loggedIn:
        client.sendNumeric(ERR_ALREADYREGISTRED)
        return

    client.username = username
    client.realname = realname
    if client.nickname is not None:
        client.login()