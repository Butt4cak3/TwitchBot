class IRCMessage:
    sender = ""
    command = ""
    params = ()

    def __init__(self, sender, command, params):
        self.sender = sender
        self.command = command
        self.params = params


class PrivMsg:
    sender = ""
    channel = ""
    text = ""

    def __init__(self, sender, channel, text):
        self.sender = sender
        self.channel = channel
        self.text = text
