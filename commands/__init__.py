def loadCommands():
    # TODO: Add ISON, USERS, WHOWAS
    import admin
    import away
    import info
    import invite
    import join
    import kick
    import kill
    import mode
    import msg
    import names
    import nick
    import oper
    import part
    import ping
    import quit
    import rehash
    import stats
    import timecmd
    import topic
    import user
    import userhost
    import version
    import wallops
    import who
    import whois

    return {'ADMIN': admin,
            'AWAY': away,
            'INFO': info,
            'INVITE': invite,
            'JOIN': join,
            'KICK': kick,
            'KILL': kill,
            'MODE': mode,
            'NAMES': names,
            'NICK': nick,
            'NOTICE': msg,
            'OPER': oper,
            'PART': part,
            'PING': ping,
            'PRIVMSG': msg,
            'QUIT': quit,
            'REHASH': rehash,
            'STATS': stats,
            'TIME': timecmd,
            'TOPIC': topic,
            'USER': user,
            'USERHOST': userhost,
            'VERSION': version,
            'WALLOPS': wallops,
            'WHO': who,
            'WHOIS': whois}