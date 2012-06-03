def loadCommands():
    import join
    import mode
    import msg
    import nick
    import oper
    import part
    import ping
    import quit
    import rehash
    import topic
    import user
    import who

    return {'JOIN': join,
            'MODE': mode,
            'NICK': nick,
            'NOTICE': msg,
            'OPER': oper,
            'PART': part,
            'PING': ping,
            'PRIVMSG': msg,
            'QUIT': quit,
            'REHASH': rehash,
            'TOPIC': topic,
            'USER': user,
            'WHO': who}