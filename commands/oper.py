def run(client, line, serverhandler):
    username = line.readWord()
    password = line.readWord()

    if client.hostname not in serverhandler.config.operhosts:
        client.sendNumeric("491", ":No O-lines for your host")
        return

    if username in serverhandler.config.opers.keys() and password == serverhandler.config.opers[username]:
        client.modes.append('o')
        client.sendNumeric("381", ":You are now an IRC operator")
    else:
        client.sendNumeric("464", ":Password incorrect")
        print username, password
        print serverhandler.config.opers
