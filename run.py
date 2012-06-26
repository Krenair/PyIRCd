import select
import signal
import socket
import sys

from classes import ServerHandler
from threading import Thread

serverhandler = ServerHandler("config.json")

oldexcepthook = sys.excepthook
def newexcepthook(type, value, tb):
    serverhandler.sigint(type)
    oldexcepthook(type, value, tb)
sys.excepthook = newexcepthook

def signal_handler(signal, frame):
    print('')
    serverhandler.sigint("SIGINT received.")
    serverhandler.run = False
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

mainserversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
mainserversocket.bind((socket.gethostname(), serverhandler.config.port))
mainserversocket.listen(1)
serverhandler.addServerSocket(mainserversocket)
host, port = mainserversocket.getsockname()

if len(serverhandler.serverSockets) < 1:
    print("Not listening on any ports, quitting.")
    sys.exit(0)
else:
    print("Listening on " + host + ":" + str(port))

if 'pyinotify' in sys.modules:
    serverhandler.moduleWatcher.start_watching()

while serverhandler.run:
    s = select.select(serverhandler.selectList, [], serverhandler.selectList, 1) # 1 as timeout so we can keep adding to the lists.
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