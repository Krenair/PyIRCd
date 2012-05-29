def run(client, line, serverhandler):
    client.writeline(":" + serverhandler.config.servername + " PONG " + serverhandler.config.servername + " " + line.text)