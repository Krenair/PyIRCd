def getCommandNames():
    return ['PING']

def run(client, line, serverhandler):
    text = line.readWord()
    if line.isMoreToRead():
        server = line.readWord()

    client.writeLine(":" + serverhandler.config.servername + " PONG " + serverhandler.config.servername + " " + text)