from numerics import RPL_ADMINME, RPL_ADMINLOC1, RPL_ADMINLOC2, RPL_ADMINEMAIL

def run(client, line, serverhandler):
    client.sendNumeric(RPL_ADMINME, serverhandler.config.servername)
    client.sendNumeric(RPL_ADMINLOC1, serverhandler.config.location)
    client.sendNumeric(RPL_ADMINLOC2, serverhandler.config.locationspecific)
    client.sendNumeric(RPL_ADMINEMAIL, serverhandler.config.adminemail)