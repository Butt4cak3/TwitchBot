from twitchbot import Plugin, Permission, Event
from collections import deque
import subprocess
import threading
import socketserver


class SongRequest(Plugin):
    def init(self):
        self.register_command("sr", self.cmd_request,
                              permissions=(Permission.Everyone,))

        config = self.get_config()
        config.setdefault("host", "localhost")
        config.setdefault("port", 9999)

        self.on_request = Event()

        self.server = ServerThread(self)
        self.server.start()

    def cmd_request(self, params, channel, sender, command):
        url = params[0]

        self.on_request.invoke(url)

        name = sender.get_displayname()
        msg = "@{} Your song was queued.".format(name)
        self.get_bot().say(channel, msg)


class ServerThread(threading.Thread):
    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin

    def run(self):
        self.server = MusicServer(self.plugin)
        self.server.serve_forever()


class MusicServer(socketserver.TCPServer):
    def __init__(self, plugin):
        self.plugin = plugin
        host = plugin.get_config().get("host")
        port = plugin.get_config().get("port")
        super().__init__((host, port), MusicConnectionHandler)


class MusicConnectionHandler(socketserver.BaseRequestHandler):
    def handle(self):
        self.server.plugin.on_request.subscribe(self.on_request)
        while True:
            data = self.request.recv(10)
            if not data:
                break

            message = data.decode("utf-8")
            if message == "quit":
                break
        self.server.plugin.on_request.unsubscribe(self.on_request)

    def on_request(self, url):
        message = url + "\n"
        self.request.sendall(message.encode("utf-8"))
