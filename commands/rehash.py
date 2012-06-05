from __init__ import loadCommands
from classes import Config

def run(client, line, serverhandler):
    serverhandler.config = Config("config.json")
    for module in serverhandler.commandMap.values():
        reload(module)

    serverhandler.commandMap = loadCommands()