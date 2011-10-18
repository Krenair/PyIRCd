from classes import Config
from classes import ServerHandler
from threading import Thread
import select
import signal
import socket
import sys

def signal_handler(signal, frame):
    serverhandler.sigint("SIGINT received.")
    run = False
    print ""
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

serverhandler = ServerHandler(Config("PyIRCd.conf"))

oldexcepthook = sys.excepthook
def newexcepthook(type, value, tb):
    serverhandler.sigint(type)
    oldexcepthook(type, value, tb)
sys.excepthook = newexcepthook

mainserversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
mainserversocket.bind((socket.gethostname(), 6667))
mainserversocket.listen(1)
serverhandler.serversockets.append(mainserversocket)

if len(serverhandler.serversockets) == 0:
    print "Not listening on any ports, quitting."
    sys.exit(0)

run = True
while run:
    for stream in select.select(serverhandler.serversockets + serverhandler.remotesockets + [sys.stdin], [], [])[0]:
        if stream in serverhandler.serversockets: #server socket returned - this must mean that here is an incoming connection
            Thread(target=serverhandler.acceptconnection, args=[stream]).start()
        else: #this must mean there is a line to be read and processed
            Thread(target=serverhandler.processline, args=[stream]).start()
mainserversocket.close()
