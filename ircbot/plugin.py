import os.path

class Plugin:
    _bot = None
    _path = None

    def __init__(self, bot, path):
        self._bot = bot
        self._path = path
        self.init()

    def init(self):
        pass

    def exit(self):
        pass

    def on_message(self, msg):
        pass

    def on_privmsg(self, privmsg):
        pass

    def get_bot(self):
        return self._bot

    def register_command(self, name, handler):
        self.get_bot().register_command(name, handler)

    def unregister_command(self, name):
        self.get_bot().unregister_command(name)

    def get_path(self, path=None):
        if path is None:
            return self._path
        else:
            return os.path.join(self._path, path)
