from twitchbot import Plugin, Permission
from collections import deque
import subprocess
import threading


class SongRequest(Plugin):
    def init(self):
        self.register_command("sr", self.cmd_request,
                              permissions=(Permission.Everyone,))
        self.player = MusicThread()

    def start_player(self, url):
        self.player = MusicThread()
        self.player.add(url)
        self.player.start()

    def cmd_request(self, params, channel, sender, command):
        url = params[0]

        if not self.player.running:
            self.start_player(url)
        else:
            self.player.add(url)

        name = sender.get_displayname()
        msg = "@{} Your song was queued.".format(name)
        self.get_bot().say(channel, msg)


class MusicThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.playlist = deque()
        self.running = False

    def run(self):
        self.running = True
        while len(self.playlist) > 0:
            url = self.playlist.popleft()
            downloader = subprocess.Popen(("youtube-dl", "--no-playlist", "-o",
                                           "-", url),
                                          stdout=subprocess.PIPE)
            player = subprocess.Popen(("mpv", "--no-video", "-"),
                                      stdin=downloader.stdout)
            downloader.wait()
            player.wait()
        self.running = False

    def add(self, url):
        self.playlist.append(url)
