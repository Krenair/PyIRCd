from classes import Config

def getCommandNames():
    return ['REHASH']

def run(client, line, serverhandler):
    serverhandler.config = Config(serverhandler.configPath)
    serverhandler.commandMap = serverhandler.loadCommands()