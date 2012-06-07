from numerics import RPL_VERSION

def run(client, line, serverhandler):
    client.sendNumeric(RPL_VERSION, "PyIRCd-" + serverhandler.version, "", serverhandler.config.servername, "")
    client.sendSupports()