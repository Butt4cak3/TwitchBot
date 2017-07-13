import pkgutil
import inspect
import irc
import plugins
from . import Plugin
import traceback
import os

class IRCBot(irc.IRCClient):
    plugins = []
    commands = {}
    command_prefix = ';'
    ops = []
    channels = []

    def __init__(self, address=None):
        super().__init__(address)
        self.load_plugins()

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
            return False

        if not inspect.isclass(constructor) or not issubclass(constructor, Plugin):
            return False

        try:
            instance = constructor(self, pluginpath)
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

            if len(privmsg['text']) > 0 and privmsg['text'][0] == self.command_prefix:
                self.handle_command(privmsg)

            for plugin in self.plugins:
                plugin.on_privmsg(privmsg)
        elif msg['command'] == '376':
            for channel in self.channels:
                self.send('JOIN {}'.format(channel))

    def handle_command(self, privmsg):
        cmd = self.parse_command(privmsg)

        if not cmd['command'] in self.commands:
            return

        if (not self.commands[cmd['command']]['oponly']) or (self.isop(cmd['sender'])):
            self.execute_command(cmd)

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

    def register_command(self, name, handler, oponly=True):
        self.commands[name] = {
            'oponly': oponly,
            'handler': handler
        }

    def unregister_command(self, name):
        self.commands.pop(name)

    def command_exists(self, name):
        return name in self.commands

    def isop(self, nick):
        return nick in self.ops

    def register(self, nick, password):
        super().register(nick, nick, nick, password)

    def send(self, message):
        print('--> {}'.format(message))
        super().send(message)

    def recv(self):
        message = super().recv()
        if message is not None and message != False:
            print('<-- {}'.format(message))
        return message
