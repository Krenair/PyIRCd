from numerics import *

def getCommandNames():
    return ['ADMIN']

def run(client, line, serverhandler):
    client.sendNumeric(RPL_ADMINME, serverhandler.config.servername)
    client.sendNumeric(RPL_ADMINLOC1, serverhandler.config.location)
    client.sendNumeric(RPL_ADMINLOC2, serverhandler.config.locationspecific)
    client.sendNumeric(RPL_ADMINEMAIL, serverhandler.config.adminemail)
