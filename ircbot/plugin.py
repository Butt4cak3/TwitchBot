class Plugin:
    _bot = None

    def __init__(self, bot):
        self._bot = bot
        self.init()

    def init(self):
        pass

    def exit(self):
        pass

    def on_message(self, msg):
        pass

    def get_bot(self):
        return self._bot
