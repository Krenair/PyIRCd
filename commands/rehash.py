from classes import Config

def getCommandNames():
    return ['REHASH']

def run(client, line, serverhandler):
    serverhandler.config = Config("config.json")
    serverhandler.commandMap = serverhandler.loadCommands()