import sys

class Config:
    def __init__(self, path):
        self.path = path

class ServerHandler:
    def __init__(self, config):
        self.config = config
        self.serversockets = []
        self.remotesockets = []
        self.socketrelations = {} #remotesocket -> serversocket

    def sigint(self, message):
        for socket in self.serversockets + self.remotesockets:
            socket.close()

    def acceptconnection(self, serversocket):
        socket = serversocket.accept()[0]
        self.socketrelations[socket] = serversocket
        self.remotesockets.append(socket)

    def processline(self, stream): #input from a socket or console
        if stream == sys.stdin: #console
            line = sys.stdin.readline()
        else: #a socket
            line = ""
            try:
                while True:
                    line += stream.recv(1)
                    if len(line) >= 2 and line[-2:] == "\r\n":
                        break
            except KeyboardInterrupt:
                pass
            #stream.send("hello world\r\n")

    def closeremotesocket(self, socket):
        del self.remotesockets[socket]
        socket.close()

class RemoteServer: #another server on the network
    pass

class RemoteClient: #an actual IRC client
    pass
