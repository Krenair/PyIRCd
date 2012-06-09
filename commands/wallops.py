from numerics import ERR_NEEDMOREPARAMS

def run(client, line, serverhandler):
    if not line.isMoreToRead():
        client.sendNumeric(ERR_NEEDMOREPARAMS, 'WALLOPS')
    else:
        message = line.readToEnd()[1:]
        for c in serverhandler.clients.values():
            if 'o' in c.modes:
                c.writeLine(":" + str(client) + " WALLOPS :" + message)