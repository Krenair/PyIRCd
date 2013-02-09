from numerics import ERR_NICKNAMEINUSE

def getCommandNames():
    return ['NICK']

def run(client, line, serverhandler):
    nickname = line.readWord()
    if line.isMoreToRead():
        hopcount = line.readWord()

    if serverhandler.getClient(nickname):
        client.sendNumeric(ERR_NICKNAMEINUSE, nickname)
        return

    client.setNickname(nickname)
    if client.username is not None and not client.loggedIn:
        client.login()
