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
            text = self.recv()
            msg = self.parse_message(text)

            if msg['command'] == 'PING':
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

    def handle_ping(self, msg):
        self.send('PONG :{}'.format(' '.join(params)))

    def privmsg(self, channel, message):
        self.conn.send('PRIVMSG {} :{}'.format(channel, message))

    def quit(self, message=''):
        self.conn.send('QUIT :{}'.format(message))

    def send(self, message):
        self.conn.send(message)

    def recv(self):
        return self.conn.recv()

    def parse_message(self, text):
        parts = text.split(' ')

        if parts[0][0] == ':':
            sender = parts.pop(0)
            bangpos = sender.find('!')
            if bangpos != -1:
                sender = sender[0:bangpos]
        else:
            sender = None

        action = parts.pop(0)

        params = []
        while len(parts) > 0:
            part = parts.pop(0)
            if len(part) > 0 and part[0] == ':':
                param = part[1:]
                while len(parts) > 0:
                    param += ' ' + parts.pop(0)
                params.append(param)
            else:
                params.append(part)

        return {
            'sender': sender,
            'command': action,
            'params': params
        }

    def parse_privmsg(self, msg):
        return {
            'sender': msg['sender'],
            'channel': msg['params'][0],
            'text': msg['params'][1]
        }

    def on_message(self, message):
        pass
