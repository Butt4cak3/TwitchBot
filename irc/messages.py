from collections import deque


class IRCMessage:
    sender = ""
    command = ""
    params = ()

    def __init__(self, sender, command, params):
        self.sender = sender
        self.command = command
        self.params = params

    @staticmethod
    def parse(raw):
        parts = deque(raw.split(" "))

        if parts[0][0] == ":":
            sender = parts.popleft()[1:]
            bangpos = sender.find("!")
            if bangpos != -1:
                sender = sender[0:bangpos]
        else:
            sender = None

        action = parts.popleft()

        params = []
        while len(parts) > 0:
            part = parts.popleft()
            if len(part) > 0 and part[0] == ":":
                param = part[1:]
                while len(parts) > 0:
                    param += " " + parts.popleft()
                params.append(param)
            else:
                params.append(part)

        return IRCMessage(sender, action, params)


class PrivMsg:
    sender = ""
    channel = ""
    text = ""

    def __init__(self, sender, channel, text):
        self.sender = sender
        self.channel = channel
        self.text = text
