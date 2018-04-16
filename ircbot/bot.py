import pkgutil
import inspect
import irc
import plugins
from . import Plugin, User
import traceback
import os

class IRCBot(irc.IRCClient):
    plugins = []
    commands = {}
    ops = []
    bots = []
    channels = []
    oauth = ''
    config = None

    def __init__(self, config):
        address = (config['address']['host'], config['address']['port'])
        super().__init__(address)
        self.set_timeout(config['connectionTimeout'])
        self.config = config
        self.load_plugins()

    def get_config(self):
        return self.config

    def load_plugins(self):
        prefix = plugins.__name__ + '.'
        for importer, modname, ispkg in pkgutil.iter_modules(plugins.__path__):
            if ispkg:
                if not self.load_plugin(modname):
                    print('Could not load plugin "{}"'.format(modname))

    def load_plugin(self, modname):
        prefix = plugins.__name__ + '.'

        try:
            package = __import__(prefix + modname, fromlist='dummy')
            pluginpath = package.__path__[0]
            constructor = getattr(package, modname)
        except:
            print(traceback.format_exc())
            return False

        if not inspect.isclass(constructor) or not issubclass(constructor, Plugin):
            return False

        if not modname in self.config['plugins']:
            self.config['plugins'][modname] = {}

        pluginconfig = self.config['plugins'][modname]

        try:
            instance = constructor(self, pluginpath, pluginconfig)
        except:
            print(traceback.format_exc())
            return False

        self.plugins.append(instance)

        return True

    def on_message(self, msg):
        for plugin in self.plugins:
            plugin.on_message(msg)

        if msg['command'] == 'PRIVMSG':
            privmsg = self.parse_privmsg(msg)

            if privmsg['sender'].is_bot():
                return

            if len(privmsg['text']) > 0 and privmsg['text'][0] == self.get_config()['commandPrefix']:
                self.handle_command(privmsg)

            for plugin in self.plugins:
                plugin.on_privmsg(privmsg)
        elif msg['command'] == '376':
            for channel in self.channels:
                self.send('JOIN {}'.format(channel))

    def handle_command(self, privmsg):
        cmd = self.parse_command(privmsg)
        sender = cmd['sender']

        if not cmd['command'] in self.commands:
            return

        permissions = self.commands[cmd['command']]['permissions']

        if sender.is_bot():
            return

        if self.has_permission(sender, permissions):
            self.execute_command(cmd)

    def has_permission(self, user, permissions):
        if user.is_op():
            return True
        elif 'everyone' in permissions:
            return True
        elif 'mod' in permissions and user.is_mod():
            return True
        elif 'broadcaster' in permissions and user.is_broadcaster():
            return True
        elif 'subscriber' in permissions and user.is_subscriber():
            return True
        else:
            return False

    def execute_command(self, cmd):
        if cmd['command'] in self.commands:
            handler = self.commands[cmd['command']]['handler']
            try:
                handler(cmd['params'], cmd['channel'], cmd['sender'], cmd['command'])
            except:
                self.privmsg(cmd['channel'], 'I tried, but something happened during the execution of that command.')
                print(traceback.format_exc())

    def parse_command(self, privmsg):
        parts = privmsg['text'].split(' ')
        command = parts.pop(0)[1:].lower()
        params = []

        while len(parts) > 0:
            part = parts.pop(0)

            if len(part) == 0:
                continue

            if part[0] == '"':
                param = part[1:]
                if param[-1] == '"':
                    param = param[0:-1]
                else:
                    while len(parts) > 0:
                        p = parts.pop(0)
                        if len(p) > 0 and p[-1] == '"':
                            param += ' ' + p[0:-1]
                            break
                        else:
                            param += ' ' + p
                params.append(param)
            else:
                params.append(part)

        return {
            'sender': privmsg['sender'],
            'channel': privmsg['channel'],
            'command': command,
            'params': params
        }

    def register_command(self, name, handler, permissions=None):
        if isinstance(permissions, str):
            permissions = (permissions,)
        elif permissions is None:
            permissions = ('broadcaster', 'mod')

        self.commands[name] = {
            'permissions': tuple(permissions),
            'handler': handler
        }

    def unregister_command(self, name):
        self.commands.pop(name)

    def command_exists(self, name):
        return name in self.commands

    def isop(self, nick):
        return nick in self.ops

    def isbot(self, nick):
        return nick in self.bots

    def register(self, nick, password):
        self.oauth = password[6:]
        super().register(nick, nick, nick, password)
        self.send('CAP REQ :twitch.tv/tags')

    def send(self, message):
        print('--> {}'.format(message))
        super().send(message)

    def recv(self):
        message = super().recv()
        if message is not None and message != False:
            print('<-- {}'.format(message))
        return message

    def parse_message(self, message):
        if message[0] == '@':
            tagstring = message[1:message.find(' ')]
            tags = self.parse_tags(tagstring)
            message = message[message.find(' ') + 1:]
        else:
            tags = {}

        result = super().parse_message(message)
        nick = result['sender']
        tags['nick'] = nick
        if 'user-id' in tags:
            result['sender'] = User(tags, self.isop(nick), self.isbot(nick))
        else:
            result['sender'] = tags

        return result

    def parse_tags(self, tagstring):
        tags = {}
        parts = tagstring.split(';')

        for part in parts:
            key, value = part.split('=')
            tags[key] = value

        return tags
