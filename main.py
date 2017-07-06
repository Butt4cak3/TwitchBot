import irc
from ircbot import IRCBot

def main():
    client = IRCBot(('irc.twitch.tv', 6667))
    client.register('', '', password='')
    client.main()

if __name__ == '__main__':
    main()
