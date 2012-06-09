from numerics import ERR_NOOPERHOST, RPL_YOUREOPER, ERR_PASSWDMISMATCH

def getCommandNames():
    return ['OPER']

def run(client, line, serverhandler):
    username = line.readWord()
    password = line.readWord()

    if client.hostname not in serverhandler.config.operhosts:
        client.sendNumeric(ERR_NOOPERHOST)
    elif username in serverhandler.config.opers.keys() and password == serverhandler.config.opers[username]:
        client.modes.append('o')
        client.sendNumeric(RPL_YOUREOPER)
    else:
        client.sendNumeric(ERR_PASSWDMISMATCH)