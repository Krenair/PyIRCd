def run(client, line, serverhandler):
    receivers = line.readWord().split(",")
    text = line.readToEnd()[1:]

    for receiver in list(set(receivers)): # Remove duplicate receivers.
        if serverhandler.isChannelName(receiver):
            channel = serverhandler.getChannel(receiver)
            if channel is None: # Channel doesn't exist.
                client.sendNumeric("401", receiver + " :No such nick/channel")
            elif 'n' in channel.modes and client not in channel.members:
                client.sendNumeric("404", receiver + " :Cannot send to channel")
            else:
                for member in channel.members:
                    member.writeLine(":" + str(client) + " PRIVMSG " + receiver + " :" + text)
        else:
            receiverClient = serverhandler.getClient(receiver)
            if receiverClient is None:
                client.sendNumeric("401", receiver + " :No such nick/channel")
            else:
                receiverClient.writeLine(":" + str(client) + " PRIVMSG " + receiver + " :" + text)