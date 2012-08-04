import datetime, time
from numerics import *

def getCommandNames():
    return ['STATS']

def run(client, line, serverhandler):
    query = line.readWord()
    if query == 'm': # Returns a list of commands supported by the server and the usage count for each if the usage count is non zero;
        for commandName, usageCount in list(serverhandler.commandUsage.items()):
            client.sendNumeric(RPL_STATSCOMMANDS, commandName, usageCount)
    elif query == 'u': # Returns a string showing how long the server has been up.
        client.sendNumeric(RPL_STATSUPTIME, str(datetime.timedelta(seconds=time.mktime(time.localtime()) - time.mktime(serverhandler.startTime))))
        client.sendNumeric(RPL_STATSCONN, serverhandler.highestConnectionCount, serverhandler.highestConnectionCount, serverhandler.connectionsReceived)
    #elif query == 'o': # Returns a list of hosts from which normal clients may become operators;
        #for host in serverhandler.config.operhosts:
            #client.sendNumeric(RPL_STATSOLINE, host, name)
            # TODO: Make a server using existing software so I can see exactly what name is
            # It's probably the OPER username, in which case I'll need to find a non-ugly way to store all three pieces of data (hostname, username, password) in an entry in a JSON list.
    #elif query == 'l': # Returns a list of the server's connections, showing how long each connection has been established and the traffic over that connection in bytes and messages for each direction;
        #for connection in connections:
            #client.sendNumeric(RPL_STATSLLINE, hostmask, servername, maxdepth)
            # TODO: Investigate what maxdepth means.
    client.sendNumeric(RPL_ENDOFSTATS, query)
