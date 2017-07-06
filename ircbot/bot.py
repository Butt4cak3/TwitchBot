import pkgutil
import inspect
import irc
import plugins
from . import Plugin

class IRCBot(irc.IRCClient):
    plugins = []

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
            constructor = getattr(package, modname)
        except:
            return False

        if not inspect.isclass(constructor) or not issubclass(constructor, Plugin):
            print(constructor)
            return False

        try:
            instance = constructor(self)
            self.plugins.append(instance)
        except:
            return False

        return True


    def on_message(self, msg):
        for plugin in self.plugins:
            plugin.on_message(msg)

    def send(self, message):
        print('--> {}'.format(message))
        super().send(message)

    def recv(self):
        message = super().recv()
        if message is not None and message != False:
            print('<-- {}'.format(message))
        return message
