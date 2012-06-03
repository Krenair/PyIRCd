import __init__
from classes import Config

def run(client, line, serverhandler):
    serverhandler.config = Config("config.json")
    for module in serverhandler.commandMap.values():
        reload(module)

    serverhandler.commandMap = __init__.loadCommands()