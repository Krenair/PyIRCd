def getCommandNames():
    return ['NICK']

def run(client, line, serverhandler):
    nickname = line.readWord()
    if line.isMoreToRead():
        hopcount = line.readWord()

    client.setNickname(nickname)
    if client.username is not None and not client.loggedIn:
        client.login()