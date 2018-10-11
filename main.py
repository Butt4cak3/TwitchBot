#!/usr/bin/python3 -u

import irc
from twitchbot import TwitchBot
import json
import os
import time

CONFIG_FILE = "config.json"


def main():
    if not os.path.isfile(CONFIG_FILE):
        with open(CONFIG_FILE, "a") as f:
            f.write("{}")

    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)

    # Twitch sends a PING about every 5 minutes, so 10 minutes should be safe
    # to assume that the connection dropped
    config.setdefault("connectionTimeout", 600)
    config.setdefault("address", {})
    config["address"].setdefault("host", "irc.twitch.tv")
    config["address"].setdefault("port", 6667)
    config.setdefault("username", "")
    config.setdefault("oauth", "")
    config.setdefault("ops", [])
    config.setdefault("channels", [])
    config.setdefault("bots", [])
    config.setdefault("plugins", {})
    config.setdefault("commandPrefix", "!")

    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, sort_keys=True, indent=4)

    if (config["username"] == "" or
            config["oauth"] == "" or
            config["address"]["host"] == "" or
            len(config["channels"]) == 0):
        print("Your configuration file is incomplete."
              " Check config.json for empty values.")
        return

    retry = True
    while retry:
        try:
            client = TwitchBot(config)
            client.register(config["username"], password=config["oauth"])
            client.ops = config["ops"]
            client.bots = config["bots"]
            client.channels = config["channels"]
            client.main()
        except KeyboardInterrupt:
            client.quit()
            retry = False
        except irc.ConnectionLostException:
            # Retry after some time
            time.sleep(60)

    with open(CONFIG_FILE, "w") as f:
        json.dump(client.get_config(), f, sort_keys=True, indent=4)


if __name__ == "__main__":
    main()
