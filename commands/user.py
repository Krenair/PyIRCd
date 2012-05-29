def run(client, line, serverhandler):
    if client.loggedIn:
        client.sendNumeric("462", ":You may not reregister")
        return

    client.username = line.username
    client.realname = line.realname
    if client.nickname is not None:
        client.login()