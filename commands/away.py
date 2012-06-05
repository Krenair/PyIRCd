from numerics import RPL_NOWAWAY, RPL_UNAWAY

def run(client, line, serverhandler):
    if line.isMoreToRead():
        client.awayMessage = line.readToEnd()[1:]
        client.sendNumeric(RPL_NOWAWAY)
    else:
        client.awayMessage = None
        client.sendNumeric(RPL_UNAWAY)