from ircbot import Plugin
import os
import json

class General(Plugin):
    DB_FILE = 'alias.json'
    alias = {}

    def init(self):
        self.register_command('say', self.cmd_say)
        self.register_command('quit', self.cmd_quit)
        self.register_command('alias', self.cmd_alias)

        self.DB_FILE = self.get_path(self.DB_FILE)

        if not os.path.isfile(self.DB_FILE):
            self.save_aliases()

        self.load_aliases()

    def save_aliases(self):
        with open(self.DB_FILE, 'w') as f:
            json.dump(self.alias, f)

    def load_aliases(self):
        with open(self.DB_FILE, 'r') as f:
            self.alias = json.load(f)

    def cmd_say(self, params, channel, sender, command):
        if params[0][0] == '#':
            target_channel = params[0]
            message = ' '.join(params[1:])
        else:
            target_channel = channel
            message = ' '.join(params)

        self.get_bot().privmsg(target_channel, message)

    def cmd_quit(self, params, channel, sender, command):
        if self.get_bot().isop(sender):
            self.get_bot().quit()

    def cmd_alias(self, params, channel, sender, command):
        cmd_name = params[0]
        cmd_params = params[1:]
        if len(params) > 1:
            if self.get_bot().command_exists(cmd_name):
                self.get_bot().privmsg(channel, 'The command "{}" already exists.'.format(cmd_name))
                return

            self.alias[cmd_name] = cmd_params
            self.register_command(cmd_name, self.cmd_custom)
        else:
            if cmd_name not in self.alias:
                self.get_bot().privmsg(channel, 'There is no alias "{}".'.format(cmd_name))
                return

            self.alias.pop(cmd_name)
            self.unregister_command(cmd_name)

        self.save_aliases()

    def cmd_custom(self, params, channel, sender, command):
        cmd = {
            'sender': sender,
            'channel': channel,
            'command': self.alias[command][0],
            'params': self.alias[command][1:]
        }
        self.get_bot().execute_command(cmd)
