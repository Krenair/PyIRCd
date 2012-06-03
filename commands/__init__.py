import join
import mode
import nick
import part
import ping
import privmsg
import topic
import user
import who

map = {'JOIN': join,
       'MODE': mode,
       'NICK': nick,
       'PART': part,
       'PING': ping,
       'PRIVMSG': privmsg,
       'TOPIC': topic,
       'USER': user,
       'WHO': who}