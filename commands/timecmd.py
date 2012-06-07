from numerics import RPL_TIME

from time import strftime

def run(client, line, serverhandler):
    client.sendNumeric(RPL_TIME, serverhandler.config.servername, strftime("%A %-e %B %Y -- %H:%M:%S %z (%Z)"))