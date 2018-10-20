import pkgutil
import inspect
import irc
import plugins
from . import Plugin, User, Permission, Command, ChatMessage, Event
import traceback
import os


class TwitchBot(irc.IRCClient):
    """An instance of a chat bot.

    Provides a way to connect to and communicate with the chat server and to
    react to certain events and commands.
    """

    def __init__(self, config):
        """Store configuration options and load plugins."""
        self.plugins = []
        self.commands = {}
        self.ops = []
        self.bots = []
        self.channels = []
        self.oauth = ""
        self.on_chatmessage = Event()

        address = (config["address"]["host"], config["address"]["port"])
        super().__init__(address)
        self.set_timeout(config["connectionTimeout"])
        self.config = config
        self.load_plugins()

    def get_config(self):
        """Return the configuration as a dict."""
        return self.config

    def load_plugins(self):
        """Load all plugins that are located in the plugin direcory."""
        for _imp, modname, ispkg in pkgutil.iter_modules(plugins.__path__):
            if ispkg:
                if not self.load_plugin(modname):
                    print("Could not load plugin \"{}\"".format(modname))

    def load_plugin(self, modname):
        """Load a specific plugin from the plugin directory."""
        prefix = plugins.__name__ + "."

        try:
            package = __import__(prefix + modname, fromlist="dummy")
            pluginpath = package.__path__[0]
            constructor = getattr(package, modname)
        except:
            print(traceback.format_exc())
            return False

        if (not inspect.isclass(constructor) or
                not issubclass(constructor, Plugin)):
            return False

        if modname not in self.config["plugins"]:
            self.config["plugins"][modname] = {}

        pluginconfig = self.config["plugins"][modname]

        try:
            instance = constructor(self, pluginpath, pluginconfig)
        except:
            print(traceback.format_exc())
            return False

        self.plugins.append(instance)

        return True

    def on_message(self, msg):
        """Handle a chat message.

        React to a few IRC commands and invoke the on_privmsg and on_message
        events.
        """
        for plugin in self.plugins:
            plugin.on_message(msg)

        if msg.command == "PRIVMSG":
            privmsg = self.parse_privmsg(msg)

            if self.isbot(privmsg.sender):
                return

            if (len(privmsg.text) > 0 and
                    privmsg.text[0] == self.get_config()["commandPrefix"]):
                self.handle_command(privmsg)

            chatmessage = ChatMessage(privmsg.sender, privmsg.channel[1:],
                                      privmsg.text)
            self.on_chatmessage.invoke(chatmessage)
        elif msg.command == "376":
            for channel in self.channels:
                self.send("JOIN #{}".format(channel))

    def handle_command(self, privmsg):
        """Parse a command message and execute it."""
        cmd = Command.from_privmsg(privmsg)
        sender = cmd.sender

        if cmd.name not in self.commands:
            return

        permissions = self.commands[cmd.name]["permissions"]

        if sender.is_bot():
            return

        if sender.has_permission(permissions):
            self.execute_command(cmd)

    def execute_command(self, cmd):
        """Check permissions and delegate command to the appropirate plugin."""
        if cmd.name in self.commands:
            handler = self.commands[cmd.name]["handler"]
            try:
                handler(cmd.params, cmd.channel,
                        cmd.sender, cmd.name)
            except:
                self.say(cmd.channel,
                         "I tried, but something happened during the"
                         " execution of that command.")
                print(traceback.format_exc())

    def register_command(self, name, handler, permissions=None):
        """Define a new command for the bot.

        A command must have a name that is used to call it with in chat. A
        command with the name "test" is called in chat with "!test", assuming
        that the command prefix is set to an exclamation point ("!").

        The permissions of the command define who is allowed to run the
        command. They must be passed as a list or tuple and contain members of
        the Permission enum.

        The handler is the function or method that will be called whenever
        a user tries to execute the command and has the appropriate permissions
        to do so. It is passed a list of command parameters, the name of the
        channel the command was issued from, a User object representing the
        caller of the command and an object holding more information about the
        command itself.
        """
        if isinstance(permissions, Permission):
            permissions = (permissions,)
        elif permissions is None:
            permissions = (Permission.Broadcaster, Permission.Moderator)

        self.commands[name] = {
            "permissions": tuple(permissions),
            "handler": handler
        }

    def unregister_command(self, name):
        """Remove the command with the given name from the bot."""
        self.commands.pop(name)

    def command_exists(self, name):
        """Check whether a command with a given name currently exists."""
        return name in self.commands

    def isop(self, nick):
        """Check whether a name is specified as an OP in the configuration."""
        return nick in self.ops

    def isbot(self, nick):
        """Check whether a name is specified as a bot in the configuration."""
        return nick in self.bots

    def say(self, channel, message):
        self.privmsg("#" + channel, message)

    def register(self, nick, password):
        """Authenticate with the chat server."""
        self.oauth = password[6:]
        super().register(nick, nick, nick, password)
        self.send("CAP REQ :twitch.tv/tags")

    def send(self, message):
        """Send a raaw message to the server."""
        if message[0:4] == "PASS":
            print("--> PASS *****")
        else:
            print("--> {}".format(message))

        super().send(message)

    def recv(self):
        """Receive a raw message from the chat server."""
        message = super().recv()
        if message is not None and message is not False:
            print("<-- {}".format(message))
        return message

    def parse_message(self, message):
        """Split a raw message up into its several parts."""
        if message[0] == "@":
            tagstring = message[1:message.find(" ")]
            tags = self.parse_tags(tagstring)
            message = message[message.find(" ") + 1:]
        else:
            tags = {}

        result = super().parse_message(message)
        nick = result.sender
        tags["nick"] = nick
        if "user-id" in tags:
            result.sender = User(tags, self.isop(nick), self.isbot(nick))
        else:
            result.sender = tags

        return result

    def parse_tags(self, tagstring):
        """Turn the tags that Twitch assigns to users into a list."""
        tags = {}
        parts = tagstring.split(";")

        for part in parts:
            key, value = part.split("=")
            tags[key] = value

        return tags
