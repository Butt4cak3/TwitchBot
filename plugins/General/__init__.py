from ircbot import Plugin

class General(Plugin):
    def init(self):
        self.register_command('quit', self.cmd_quit)

    def cmd_quit(self, params, channel, sender, command):
        if self.get_bot().isop(sender):
            self.get_bot().quit()
