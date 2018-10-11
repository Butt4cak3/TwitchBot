from twitchbot import Plugin, Permission
import requests
import time
import html
import json
import re


class LinkPreview(Plugin):
    lastresponse = 0
    RESPONSE_INTERVAL = 20
    enabled = True
    ignored = []

    def init(self):
        self.register_command("linkpreview", self.cmd_linkpreview)
        self.get_config().setdefault("previewLinks",
                                     [Permission.Broadcaster,
                                      Permission.Moderator])
        self.get_config().setdefault("enabled", True)
        self.get_config().setdefault("ignored_urls", [])
        self.enabled = self.get_config().get("enabled")
        self.ignored = self.get_config().get("ignored_urls")
        self.get_bot().on_chatmessage.subscribe(self.on_chatmessage)

    def on_chatmessage(self, msg):
        if not self.enabled:
            return

        now = int(time.time())
        if now < self.lastresponse + self.RESPONSE_INTERVAL:
            return

        sender = msg.sender
        permission = Permission.from_strings(self.get_config()["previewLinks"])
        if not sender.has_permission(permission):
            return

        match = re.search(r"https?://\S+", msg.text)
        if match is None:
            return

        url = match.group(0)

        for pattern in self.ignored:
            if re.search(pattern, url) is not None:
                return

        title = self.get_site_title(url)

        if title is None:
            return

        channel = msg.channel
        self.get_bot().say(channel, "Link description: {}".format(title))
        self.lastresponse = now

    def get_site_title(self, url):
        request = requests.get(url)
        response = request.text

        # Don"t do this at home! Parsing HTML with regular expressions is bad.
        # But I"m also lazy, so screw it...
        match = re.search(r"<\s*title[^>]*>([^<]+)<\s*/\s*title\s*>", response)

        if match is not None:
            return match.group(1)
        else:
            return None

    def cmd_linkpreview(self, params, channel, sender, command):
        if len(params) > 0:
            mode = params[0].lower()
        else:
            mode = ""

        if mode in ["yes", "enable", "enabled", "on", "1", "true", "y"]:
            self.enable_response()
        else:
            self.disable_response()

    def enable_response(self):
        self.enabled = True

    def disable_response(self):
        self.enabled = False
