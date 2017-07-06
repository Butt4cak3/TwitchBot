from . import IRCConnection
import queue

class IRCClient:
    conn = IRCConnection()
    msg_buffer = queue.Queue()

    def __init__(self, address=None):
        if address is not None:
            self.connect(address)

    def main(self):
        while True:
            msg = self.recv()
            if msg[0:4] == 'PING':
                self.handle_ping(msg)
            self.on_message(msg)

    def connect(self, address):
        self.conn.connect(address)
        self.conn.setblocking(True)

    def disconnect(self):
        self.conn.close()

    def register(self, nick, user, realname=None, password=None):
        if realname is None:
            realname = user

        if password is not None:
            self.send('PASS {}'.format(password))

        self.send('NICK {}'.format(nick))
        self.send('USER {} {} {} :{}'.format(user, user, user, realname))

    def privmsg(self, channel, message):
        self.conn.send('PRIVMSG {} :{}'.format(channel, message))

    def quit(self, message=''):
        self.conn.send('QUIT :{}'.format(message))

    def send(self, message):
        self.conn.send(message)

    def recv(self):
        return self.conn.recv()

    def on_message(self, message):
        pass
