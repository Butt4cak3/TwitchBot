from ircbot import Plugin
import sqlite3
import os
from time import gmtime, strftime

class Stats(Plugin):
    DB_FILE = 'stats.sqlite'

    db = None

    def init(self):
        self.DB_FILE = self.get_path(self.DB_FILE)
        init_db = not os.path.isfile(self.DB_FILE)
        self.db = sqlite3.connect(self.DB_FILE)
        if init_db:
            self.init_db()

    def init_db(self):
        c = self.db.cursor()
        c.execute('''
        CREATE TABLE privmsg (
            time TEXT,
            sender TEXT,
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
        values = (
            strftime('%Y-%m-%d %H:%M:%S', gmtime()),
            msg['sender'],
            msg['channel'],
            msg['text']
        )
        c.execute('INSERT INTO privmsg (time, sender, channel, content) VALUES (?, ?, ?, ?)', values)
        c.close()
        self.db.commit()
