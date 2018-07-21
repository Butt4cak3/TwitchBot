from . import IRCConnection
from . import ConnectionLostException
from collections import deque
import time

class IRCClient:
    conn = IRCConnection()
    timeout = 600
    last_message = int(time.time())
    address = None

    def __init__(self, address=None):
        if address is not None:
            self.connect(address)

    def main(self):
        while True:
            text = self.recv()

            if text == False:
                raise ConnectionLostException('recv returned False')

            now = int(time.time())

            if (text == False) or (text == ''):
                if now >= self.last_message + self.timeout:
                    self.reconnect()
                else:
                    continue

            self.last_message = now

            msg = self.parse_message(text)

            if msg['command'] == 'PING':
                self.handle_ping(msg)

            self.on_message(msg)

    def connect(self, address):
        self.address = address
        self.conn.connect(address)
        self.conn.setblocking(True)
        self.conn.settimeout(600)

    def disconnect(self):
        self.conn.close()

    def reconnect(self):
        self.disconnect()
        self.connect(self.address)

    def set_timeout(self, seconds):
        self.timeout = seconds
        self.conn.settimeout(seconds + 1)
        pass

    def register(self, nick, user, realname=None, password=None):
        if realname is None:
            realname = user

        if password is not None:
            self.send('PASS {}'.format(password))

        self.send('NICK {}'.format(nick))
        self.send('USER {} {} {} :{}'.format(user, user, user, realname))

    def handle_ping(self, msg):
        self.send('PONG :{}'.format(' '.join(msg['params'])))

    def privmsg(self, channel, message):
        self.send('PRIVMSG {} :{}'.format(channel, message))

    def quit(self, message=''):
        self.send('QUIT :{}'.format(message))
        self.disconnect()

    def send(self, message):
        self.conn.send(message)

    def recv(self):
        return self.conn.recv()

    def parse_message(self, text):
        parts = deque(text.split(' '))

        if parts[0][0] == ':':
            sender = parts.popleft()
            sender = sender[1:]
            bangpos = sender.find('!')
            if bangpos != -1:
                sender = sender[0:bangpos]
        else:
            sender = None

        action = parts.popleft()

        params = []
        while len(parts) > 0:
            part = parts.popleft()
            if len(part) > 0 and part[0] == ':':
                param = part[1:]
                while len(parts) > 0:
                    param += ' ' + parts.popleft()
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
