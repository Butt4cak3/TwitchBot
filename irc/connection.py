import socket

class IRCConnection:
    sock = None

    def __init__(self, address=None):
        if address is not None:
            self.connect(address)

    def connect(self, address):
        self.sock = socket.create_connection(address)

    def close(self):
        self.sock.close()

    def recv(self):
        # Find out the length of the next message by peeking
        try:
            buf = self.sock.recv(511, socket.MSG_PEEK)
        except:
            return False

        if not buf:
            return False
        text = buf.decode(errors='ignore')
        msg_len = text.find('\r\n') + 2

        # Now get the actual next message
        buf = self.sock.recv(msg_len)
        text = buf.decode(errors='ignore')
        while text[-2:] != '\r\n':
            buf = self.sock.recv(1)
            text += buf.decode(errors='ignore')
        text = text[:-2]

        if len(text) > 0:
            return text
        else:
            return None

    def send(self, text):
        text = text.replace('\r', '').replace('\n', '')
        text = text + '\r\n'

        if len(text) > 512:
            return False

        buf = str.encode(text)

        self.sock.send(buf)
        return True

    def setblocking(self, mode):
        self.sock.setblocking(mode)

    def settimeout(self, s):
        self.sock.settimeout(s)

def connect(address):
    return Connection(address)
