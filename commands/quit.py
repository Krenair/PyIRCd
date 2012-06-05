def run(client, line, serverhandler):
    if line.isMoreToRead():
        message = "Quit: " + line.readToEnd()[1:]
    else:
        message = "Client quit"

    serverhandler.socketDisconnected(client.socket, message)