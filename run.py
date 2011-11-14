from classes import Config
from classes import ServerHandler
from threading import Thread
import select
import signal
import socket
import sys

oldexcepthook = sys.excepthook
def newexcepthook(type, value, tb):
    oldexcepthook(type, value, tb)
    serverhandler.sigint(type)
sys.excepthook = newexcepthook

serverhandler = ServerHandler(Config("PyIRCd.conf"))

def signal_handler(signal, frame):
    serverhandler.sigint("SIGINT received.")
    serverhandler.run = False
    print ""
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

mainserversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
mainserversocket.bind((socket.gethostname(), 6667))
mainserversocket.listen(1)
serverhandler.addserversocket(mainserversocket)

if serverhandler.serversockets == []:
    print "Not listening on any ports, quitting."
    sys.exit(0)

while serverhandler.run:
    s = select.select(serverhandler.selectlist, [], serverhandler.selectlist, 1) #1 as timeout so we can keep adding to the lists
    for stream in s[0]: #reads
        if stream in serverhandler.serversockets: #server socket returned - this must mean that here is an incoming connection
            Thread(target=serverhandler.acceptconnection, args=[stream]).start()
        elif stream not in serverhandler.readingfromsockets: #this must mean there is a line to be read and processed
            Thread(target=serverhandler.readline, args=[stream]).start()
    
    for stream in s[2]: #errors
        Thread(target=serverhandler.clientdisconnected, args=[stream]).start()
mainserversocket.close()
