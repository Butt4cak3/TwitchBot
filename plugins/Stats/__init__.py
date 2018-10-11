from ircbot import Plugin
import sqlite3
import os
from time import gmtime, strftime


class Stats(Plugin):
    DB_FILE = "stats.sqlite"

    db = None

    def init(self):
        self.get_config().setdefault("db_file", self.get_path(self.DB_FILE))

        self.DB_FILE = self.get_config()["db_file"]
        init_db = not os.path.isfile(self.DB_FILE)
        self.db = sqlite3.connect(self.DB_FILE)
        if init_db:
            self.init_db()

        self.register_command("count", self.cmd_count,
                              permissions=("mod", "broadcaster"))
        self.get_bot().on_chatmessage.subscribe(self.on_chatmessage)

    def init_db(self):
        c = self.db.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS privmsg (
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
        """)
        c.execute("""
        CREATE TABLE IF NOT EXISTS counter (
            channel TEXT,
            name TEXT,
            value NUMBER,
            PRIMARY KEY (channel, name)
        )
        """)
        self.db.commit()
        c.close()

    def on_chatmessage(self, message):
        self.save_chatmessage(message)

    def save_chatmessage(self, msg):
        c = self.db.cursor()
        sender = msg.sender
        values = (
            strftime("%Y-%m-%d %H:%M:%S", gmtime()),
            sender.get_id(),
            sender.get_name(),
            sender.get_displayname(),
            1 if sender.is_mod() else 0,
            1 if sender.is_subscriber() else 0,
            1 if sender.is_bot() else 0,
            1 if sender.is_broadcaster() else 0,
            msg.channel,
            msg.text
        )
        sql = """
        INSERT INTO privmsg (
            time, userid, name, displayname, mod, subscriber, bot,
            broadcaster, channel, content)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        c.execute(sql, values)
        c.close()
        self.db.commit()

    def cmd_count(self, params, channel, sender, command):
        if len(params) < 1:
            return

        name = params[0]

        if len(params) == 3:
            modifier = params[1]
            num = int(params[2])
        else:
            modifier = "add"
            num = 1

        c = self.db.cursor()
        sql = """
        INSERT OR IGNORE INTO counter (channel, name, value)
        VALUES (?, ?, ?)
        """
        c.execute(sql, (channel, name, 0))

        if modifier == "add":
            sql = """
            UPDATE counter SET value = value + ? WHERE channel = ? AND name = ?
            """
            c.execute(sql, (num, channel, name))
        elif modifier == "set":
            sql = "UPDATE counter SET value = ? WHERE channel = ? AND name = ?"
            c.execute(sql, (num, channel, name))

        sql = "SELECT value FROM counter WHERE channel = ? AND name = ?"
        c.execute(sql, (channel, name))
        rows = c.fetchall()
        c.close()
        self.db.commit()

        msg = "{} counter is at {}".format(name, rows[0][0])
        self.get_bot().privmsg(channel, msg)
