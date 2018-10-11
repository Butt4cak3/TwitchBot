import os.path


class Plugin:
    """This is a base class that all plugins have to inherit.

    It has methods to load and unload the plugin and provides ways to react
    to commands and chat messages.
    """
    _bot = None
    _path = None

    def __init__(self, bot, path, config):
        """Store some information and call self.init().

        Do not overwrite this. Plugin initialization code goes into the init
        method (without underscores).
        """
        self._bot = bot
        self._path = path
        self._config = config
        self.init()

    def init(self):
        """Set up everything that's needed by the plugin.

        Register commands, initialize databases and configuration here.
        """
        pass

    def exit(self):
        pass

    def on_message(self, msg):
        """Handle a parsed raw message from the server.

        This method get called every time the bot receives a message from the
        chat server. If you only want to handle actual chat messages from
        users, then use on_privmsg instead.
        """
        pass

    def on_privmsg(self, privmsg):
        """Handle a parsed chat message from.

        The privmsg dict contains a "sender", "channel" and "text".
        """
        pass

    def get_bot(self):
        """Return the bot instance that this is a plugin of."""
        return self._bot

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
        self.get_bot().register_command(name, handler, permissions)

    def unregister_command(self, name):
        """Remove the command with the given name from the bot."""
        self.get_bot().unregister_command(name)

    def get_path(self, path=None):
        """Return the absolute path of this plugin's directory.

        This can be used to store database files or similar in the directory
        the plugin is in.
        """
        if path is None:
            return self._path
        else:
            return os.path.join(self._path, path)

    def get_config(self):
        """Return the plugin's configuration.

        The configuration is stored in the bot's configuration file under
        the key "plugins".
        """
        return self._config
