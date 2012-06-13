import time

from numerics import RPL_TIME

def getCommandNames():
    return ['TIME']

def run(client, line, serverhandler):
    client.sendNumeric(RPL_TIME, serverhandler.config.servername, time.strftime("%A %-e %B %Y -- %H:%M:%S %z (%Z)"))