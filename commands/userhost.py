from numerics import ERR_NEEDMOREPARAMS, RPL_USERHOST

def run(client, line, serverhandler):
    if not line.isMoreToRead():
        client.sendNumeric(ERR_NEEDMOREPARAMS, 'USERHOST')
    else:
        result = ''
        for targetNickname in line.readToEnd().split(" "):
            targetClient = serverhandler.getClient(targetNickname)
            if targetClient is not None:
                result += targetNickname

                if 'o' in targetClient.modes:
                    result += '*'

                result += '='

                if targetClient.awayMessage is None:
                    result += '+'
                else:
                    result += '-'

                result += targetClient.username + '@' + targetClient.hostname + ' '
        client.sendNumeric(RPL_USERHOST, result[:-1])