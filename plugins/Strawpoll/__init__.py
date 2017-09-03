from ircbot import Plugin
import requests
import time
import html
import json

class Strawpoll(Plugin):
    lastresponse = 0
    RESPONSE_INTERVAL = 20

    def init(self):
        self.register_command('strawpoll', self.cmd_strawpoll)
        self.get_config().setdefault('previewLinks', [ 'broadcaster', 'moderator' ])

    def on_privmsg(self, msg):
        now = int(time.time())
        if now < self.lastresponse + self.RESPONSE_INTERVAL:
            return

        sender = msg['sender']

        if self.get_bot().has_permission(sender, self.get_config()['previewLinks']):
            self.show_info(msg['text'][24:], msg['channel'])
            self.lastresponse = now

    def show_info(self, poll_id, channel):
        request = requests.get('https://strawpoll.me/api/v2/polls/{}'.format(poll_id))
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

        request = requests.post('https://strawpoll.me/api/v2/polls', data=payload)
        response = request.json()

        self.get_bot().privmsg(channel, 'https://strawpoll.me/{}'.format(response['id']))
