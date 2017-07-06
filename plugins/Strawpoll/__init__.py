from ircbot import Plugin
import requests
import time
import html

class Strawpoll(Plugin):
    lastresponse = 0
    RESPONSE_INTERVAL = 20

    def on_privmsg(self, msg):
        now = int(time.time())
        if now < self.lastresponse + self.RESPONSE_INTERVAL:
            return

        if self.get_bot().isop(msg['sender']) and msg['text'][0:24] == 'http://www.strawpoll.me/':
            self.show_info(msg['text'][24:], msg['channel'])
            self.lastresponse = now

    def show_info(self, poll_id, channel):
        request = requests.get('https://strawpoll.me/api/v2/polls/{}'.format(poll_id))
        response = request.json()

        title = response['title']
        options = [ html.unescape(o) for o in response['options'] ]
        options = ' | '.join(options)

        self.get_bot().privmsg(channel, '[Strawpoll] {} -- {}'.format(title, options))
