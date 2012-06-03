import classes

def run(client, line, serverhandler): # TODO
    changes = []
    to = line.readWord()
    split = line.readToEnd().split(" ")
    paramindex = 1
    for char in split[0]:
        if char is "+":
            give = True
        elif char is "-":
            give = False
        elif char in ["o", "v", "h", "q", "a"]:
            changes.append(classes.ModeChange(to, client, char, give, split[paramindex]))
            paramindex += 1
        else:
            changes.append(classes.ModeChange(to, client, char, give))