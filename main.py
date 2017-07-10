#!/usr/bin/python3

import irc
from ircbot import IRCBot
import json
import os

CONFIG_FILE = 'config.json'

def main():
    if not os.path.isfile(CONFIG_FILE):
        with open(CONFIG_FILE, 'a') as f:
            f.write('{}')

    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)

    if 'address' not in config:
        config['address'] = {}

    if 'host' not in config['address']:
        config['address']['host'] = 'irc.twitch.tv'
    if 'port' not in config['address']:
        config['address']['port'] = 6667

    if 'username' not in config:
        config['username'] = ''
    if 'oauth' not in config:
        config['oauth'] = ''

    if 'ops' not in config:
        config['ops'] = []

    if 'channels' not in config:
        config['channels'] = []

    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, sort_keys=True, indent=4)

    if ((config['username'] == '')
     or (config['oauth'] == '')
     or (config['address']['host'] == '')
     or (len(config['channels']) == 0)):
        print('Your configuration file is incomplete. Check config.json for empty values.')
        return

    client = IRCBot((config['address']['host'], config['address']['port']))
    client.register(config['username'], password=config['oauth'])
    client.ops = config['ops']
    client.channels = config['channels']

    try:
        client.main()
    except KeyboardInterrupt:
        client.quit()

if __name__ == '__main__':
    main()
