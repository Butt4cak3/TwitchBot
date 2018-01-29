from ircbot import Plugin
import requests
import time
import html
import json

class Strawpoll(Plugin):
    lastresponse = 0
    RESPONSE_INTERVAL = 20
    enabled = True

    def init(self):
        self.register_command('strawpoll', self.cmd_strawpoll)
        self.get_config().setdefault('previewLinks', [ 'broadcaster', 'moderator' ])
        self.get_config().setdefault('enabled', True)
        self.enabled = self.get_config().get('enabled')

    def on_privmsg(self, msg):
        if not self.enabled:
            return

        now = int(time.time())
        if now < self.lastresponse + self.RESPONSE_INTERVAL:
            return

        if msg['text'][0:24] != 'http://www.strawpoll.me/':
            return

        sender = msg['sender']

        if self.get_bot().has_permission(sender, self.get_config()['previewLinks']):
            self.show_info(msg['text'][24:], msg['channel'])
            self.lastresponse = now

    def show_info(self, poll_id, channel):
        request = requests.get('https://www.strawpoll.me/api/v2/polls/{}'.format(poll_id))
        response = request.json()

        title = response['title']
        options = [ html.unescape(o) for o in response['options'] ]
        options = ' | '.join(options)

        self.get_bot().privmsg(channel, '[Strawpoll] {} -- {}'.format(title, options))

    def cmd_strawpoll(self, params, channel, sender, command):
        if len(params) < 3:
            self.get_bot().privmsg(channel, 'To create a poll, you have to provide a title and at least two optoins.')
            return

        poll = {
            'title': params[0],
            'options': params[1:]
        }

        payload = json.dumps(poll)

        request = requests.post('https://www.strawpoll.me/api/v2/polls', data=payload)
        response = request.json()

        self.get_bot().privmsg(channel, 'https://www.strawpoll.me/{}'.format(response['id']))
