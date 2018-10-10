class ChatMessage:
    sender = None
    channel = ""
    text = ""

    def __init__(self, sender, channel, text):
        self.sender = sender
        self.channel = channel
        self.text = text


class Command:
    name = ""
    params = ()
    sender = ""
    channel = None

    def __init__(self, name, params, sender, channel):
        self.name = name
        self.params = params
        self.sender = sender
        self.channel = channel

    @staticmethod
    def from_privmsg(privmsg):
        message = privmsg.text
        parts = message.split(" ")
        name = parts.pop(0)[1:].lower()
        params = []

        while len(parts) > 0:
            part = parts.pop(0)

            if len(part) == 0:
                continue

            if part[0] == "\"":
                param = part[1:]
                if param[-1] == "\"":
                    param = param[:-1]
                else:
                    while len(parts) > 0:
                        p = parts.pop(0)
                        if len(p) > 0 and p[-1] == "\"":
                            param += " " + p[:-1]
                            break
                        else:
                            param += " " + p
                params.append(param)
            else:
                params.append(part)

        return Command(name, params, privmsg.sender, privmsg.channel[1:])
