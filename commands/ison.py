from numerics import ERR_NEEDMOREPARAMS, RPL_ISON

def getCommandNames():
    return ['ISON']

def run(client, line, serverhandler):
    if not line.isMoreToRead():
        client.sendNumeric(ERR_NEEDMOREPARAMS, 'ISON')
    else:
        result = ''
        for targetNickname in line.readToEnd().split(" "):
            if serverhandler.getClient(targetNickname) is not None:
                result += targetNickname + ' '

        if len(result) > 0:
            result = result[:-1] # Strip any trailing whitespace.

        client.sendNumeric(RPL_ISON, result)