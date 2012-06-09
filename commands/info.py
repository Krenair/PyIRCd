from numerics import RPL_INFO, RPL_ENDOFINFO

from time import strftime

def getCommandNames():
    return ['INFO']

def run(client, line, serverhandler):
    for line in open('pyircd.info').read().splitlines():
        client.sendNumeric(RPL_INFO, line)
    client.sendNumeric(RPL_INFO, "Birth Date: " + strftime('%a %-e %b %G at %H:%M:%S %Z', serverhandler.creationTime))
    client.sendNumeric(RPL_INFO, "On-line since " + strftime('%a %-e %b %G at %H:%M:%S %Z', serverhandler.startTime))
    client.sendNumeric(RPL_ENDOFINFO)