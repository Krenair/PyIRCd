from classes import ServerHandler
from threading import Thread
from select import select
from signal import signal, SIGINT
from socket import gethostname, socket, AF_INET, SOCK_STREAM
from sys import excepthook, exit

serverhandler = ServerHandler("config.json")

oldexcepthook = excepthook
def newexcepthook(type, value, tb):
    serverhandler.sigint(type)
    oldexcepthook(type, value, tb)
excepthook = newexcepthook

def signal_handler(signal, frame):
    print ''
    serverhandler.sigint("SIGINT received.")
    serverhandler.run = False
    exit(0)
signal(SIGINT, signal_handler)

mainserversocket = socket(AF_INET, SOCK_STREAM)
mainserversocket.bind((gethostname(), serverhandler.config.port))
mainserversocket.listen(1)
serverhandler.addServerSocket(mainserversocket)
host, port = mainserversocket.getsockname()
print "Listening on " + host + ":" + str(port)

if len(serverhandler.serverSockets) < 1:
    print "Not listening on any ports, quitting."
    exit(0)

while serverhandler.run:
    s = select(serverhandler.selectList, [], serverhandler.selectList, 1) # 1 as timeout so we can keep adding to the lists.
    if not serverhandler.run:
        break

    for stream in s[0]: # Reads.
        if stream in serverhandler.serverSockets: # Server socket returned - this must mean that here is an incoming connection.
            Thread(target=serverhandler.acceptConnection, args=[stream]).start()
        elif stream not in serverhandler.readingFromSockets: # This must mean there is a line to be read and processed.
            serverhandler.readingFromSockets.append(stream)
            Thread(target=serverhandler.readLine, args=[stream]).start()
    
    for stream in s[2]: # Errors.
        Thread(target=serverhandler.socketDisconnected, args=[stream]).start()