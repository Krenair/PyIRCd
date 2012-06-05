from numerics import ERR_NOSUCHNICK, ERR_CANNOTSENDTOCHAN, RPL_AWAY

def run(client, line, serverhandler):
    receivers = line.readWord().split(",")
    text = line.readToEnd()[1:]

    for receiver in list(set(receivers)): # Remove duplicate receivers.
        if serverhandler.isChannelName(receiver):
            channel = serverhandler.getChannel(receiver)
            if channel is None: # Channel doesn't exist.
                client.sendNumeric(ERR_NOSUCHNICK, receiver)
            elif 'n' in channel.modes and client not in channel.members:
                client.sendNumeric(ERR_CANNOTSENDTOCHAN, receiver)
            else:
                for member in channel.members:
                    member.writeLine(":" + str(client) + " " + line.firstWord + " " + receiver + " :" + text)
        else:
            receiverClient = serverhandler.getClient(receiver)
            if receiverClient is None:
                client.sendNumeric(ERR_NOSUCHNICK, receiver)
            else:
                if receiverClient.awayMessage is not None:
                    client.sendNumeric(RPL_AWAY, receiverClient.nickname, receiverClient.awayMessage)

                receiverClient.writeLine(":" + str(client) + " " + line.firstWord + " " + receiver + " :" + text)