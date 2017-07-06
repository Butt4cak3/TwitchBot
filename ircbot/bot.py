import pkgutil
import inspect
import irc
import plugins
from . import Plugin
import traceback

class IRCBot(irc.IRCClient):
    DEFAULT_CHANNEL = ''
    plugins = []
    commands = {}
    command_prefix = ';'

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

            if privmsg['text'][0] == self.command_prefix:
                self.handle_command(privmsg)

            for plugin in self.plugins:
                plugin.on_privmsg(privmsg)
        elif msg['command'] == '376':
            self.send('JOIN {}'.format(self.DEFAULT_CHANNEL))

    def handle_command(self, privmsg):
        cmd = self.parse_command(privmsg)

        if cmd['command'] in self.commands:
            self.commands[cmd['command']](cmd['params'], cmd['channel'], cmd['sender'], cmd['command'])

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

    def register_command(self, name, handler):
        self.commands[name] = handler

    def send(self, message):
        print('--> {}'.format(message))
        super().send(message)

    def recv(self):
        message = super().recv()
        if message is not None and message != False:
            print('<-- {}'.format(message))
        return message
