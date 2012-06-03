import __init__

def run(client, line, serverhandler):
    #TODO: Reload all the modules and configuration files.
    serverhandler.commandMap = __init__.loadCommands()