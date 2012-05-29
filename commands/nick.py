def run(client, line, serverhandler):
    client.setNickname(line.nickname)
    if client.username is not None and not client.loggedIn:
        client.login()