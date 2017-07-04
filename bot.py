import irc

class IRCBot(irc.IRCClient):
    def on_message(self, msg):
        pass

    def send(self, message):
        print('--> {}'.format(message))
        super().send(message)

    def recv(self):
        message = super().recv()
        if message is not None and message != False:
            print('<-- {}'.format(message))
        return message
