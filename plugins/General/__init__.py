from ircbot import Plugin
import os
import json
import re
import requests
import datetime

class General(Plugin):
    DB_FILE = 'alias.json'
    alias = {}

    def init(self):
        self.register_command('help', self.cmd_help, False)
        self.register_command('commands', self.cmd_help, False)
        self.register_command('say', self.cmd_say, True)
        self.register_command('quit', self.cmd_quit, True)
        self.register_command('alias', self.cmd_alias, True)
        self.register_command('uptime', self.cmd_uptime, False)

        self.DB_FILE = self.get_path(self.DB_FILE)

        if not os.path.isfile(self.DB_FILE):
            self.save_aliases()

        self.load_aliases()

    def save_aliases(self):
        with open(self.DB_FILE, 'w') as f:
            json.dump(self.alias, f)

    def load_aliases(self):
        for alias in self.alias:
            self.unregister_command(alias)

        with open(self.DB_FILE, 'r') as f:
            self.alias = json.load(f)

        for alias in self.alias:
            self.register_command(alias, self.cmd_custom, False)

    def cmd_help(self, params, channel, sender, command):
        bot = self.get_bot()
        cmds = []
        for cmd in bot.commands:
            cmds.append(bot.command_prefix + cmd)

        bot.privmsg(channel, 'Available commands: {}'.format(' '.join(cmds)))

    def cmd_say(self, params, channel, sender, command):
        if params[0][0] == '#':
            target_channel = params[0]
            message = ' '.join(params[1:])
        else:
            target_channel = channel
            message = ' '.join(params)

        self.get_bot().privmsg(target_channel, message)

    def cmd_quit(self, params, channel, sender, command):
        self.get_bot().quit()

    def cmd_alias(self, params, channel, sender, command):
        cmd_name = params[0]
        cmd_params = params[1:]
        if len(params) > 1:
            if self.get_bot().command_exists(cmd_name):
                self.get_bot().privmsg(channel, 'The command "{}" already exists.'.format(cmd_name))
                return

            self.alias[cmd_name] = cmd_params
            self.register_command(cmd_name, self.cmd_custom, False)
        else:
            if cmd_name not in self.alias:
                self.get_bot().privmsg(channel, 'There is no alias "{}".'.format(cmd_name))
                return

            self.alias.pop(cmd_name)
            self.unregister_command(cmd_name)

        self.save_aliases()

    def cmd_custom(self, params, channel, sender, command):
        def replace_placeholder(match):
            name = match.group(1)
            if name.isdigit():
                name = int(name)
                if len(params) < name:
                    return '?'
                else:
                    return params[name - 1]
            elif name == 'u':
                return sender
            elif name == 'c':
                return channel[1:]

        cmd = {
            'sender': sender,
            'channel': channel,
            'command': self.alias[command][0],
            'params': self.alias[command][1:]
        }

        for i in range(len(cmd['params'])):
            cmd['params'][i] = re.sub('\$([cu]|[1-9][0-9]*)', replace_placeholder, cmd['params'][i])

        self.get_bot().execute_command(cmd)

    def cmd_uptime(self, params, channel, sender, command):
        streamer = channel[1:]
        url = 'https://api.twitch.tv/kraken/streams/{}'.format(streamer)
        headers = {
            'Accept': 'application/vnd.twitchtv.v3+json',
            'Authorization': 'OAuth {}'.format(self.get_bot().oauth)
        }
        request = requests.get(url, headers=headers)
        response = request.json()

        if response['stream'] is not None:
            start = datetime.datetime.strptime(response['stream']['created_at'], '%Y-%m-%dT%H:%M:%SZ')
            now = datetime.datetime.utcnow()
            uptime = now - start
            seconds = uptime.seconds
            hours = seconds // 3600
            seconds -= hours * 3600
            minutes = seconds // 60
            seconds -= minutes * 60
            self.get_bot().privmsg(channel, 'Uptime: {} hours, {} minutes'.format(hours, minutes))
        else:
            self.get_bot().privmsg(channel, '{} is currently offline.'.format(streamer))
