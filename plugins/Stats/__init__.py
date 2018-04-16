from ircbot import Plugin
import sqlite3
import os
from time import gmtime, strftime

class Stats(Plugin):
    DB_FILE = 'stats.sqlite'

    db = None

    def init(self):
        self.get_config().setdefault('db_file', self.get_path(self.DB_FILE))

        self.DB_FILE = self.get_config()['db_file']
        init_db = not os.path.isfile(self.DB_FILE)
        self.db = sqlite3.connect(self.DB_FILE)
        if init_db:
            self.init_db()

    def init_db(self):
        c = self.db.cursor()
        c.execute('''
        CREATE TABLE privmsg (
            time TEXT,
            userid NUMBER,
            name TEXT,
            displayname TEXT,
            mod NUMBER,
            subscriber NUMBER,
            bot NUMBER,
            broadcaster NUMBER,
            channel TEXT,
            content TEXT
        )
        ''')
        self.db.commit()
        c.close()

    def on_privmsg(self, privmsg):
        self.save_privmsg(privmsg)

    def save_privmsg(self, msg):
        c = self.db.cursor()
        sender = msg['sender']
        values = (
            strftime('%Y-%m-%d %H:%M:%S', gmtime()),
            sender.get_id(),
            sender.get_name(),
            sender.get_displayname(),
            1 if sender.is_mod() else 0,
            1 if sender.is_subscriber() else 0,
            1 if sender.is_bot() else 0,
            1 if sender.is_broadcaster() else 0,
            msg['channel'],
            msg['text']
        )
        c.execute('INSERT INTO privmsg (time, userid, name, displayname, mod, subscriber, bot, broadcaster, channel, content) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', values)
        c.close()
        self.db.commit()
