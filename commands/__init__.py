def loadCommands():
    import join
    import mode
    import msg
    import nick
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
            'PART': part,
            'PING': ping,
            'PRIVMSG': msg,
            'QUIT': quit,
            'REHASH': rehash,
            'TOPIC': topic,
            'USER': user,
            'WHO': who}