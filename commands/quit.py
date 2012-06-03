def run(client, line, serverhandler):
    if line.isMoreToRead():
        message = "Quit: " + line.readToEnd()[1:]
    else:
        message = "Client quit"

    clientsToNotify = []
    for channel in client.channels:
        for member in channel.members:
            if member not in clientsToNotify:
                clientsToNotify.append(member)

    for clientToNotify in clientsToNotify:
        clientToNotify.writeLine(str(client) + " QUIT :" + message)

    serverhandler.clientDisconnected(client.socket)