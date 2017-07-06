from ircbot import Plugin

class General(Plugin):
    def init(self):
        self.register_command('quit', self.cmd_quit)

    def cmd_quit(self, params, channel, sender, command):
        self.get_bot().quit()
