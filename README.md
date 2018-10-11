# Bottercak3

This is an open source chat bot that anyone can run on their own computer or
on a server. The goal is to have a bot that one can easily extend with custom
functionality beyond just replying to commands with simple messages. The way
I'm trying to achieve that is throught a plugin system.

## Setup

In order to run the bot, you have to have [Python](https://www.python.org)
installed. If you're on Windows, make sure you tick the box "Add Python to
PATH" during the installation.

Once you have Python installed, you also need an additional package for Python
that the bot needs to run. It's called "requests" and you install it by opening
a terminal and running `pip install requests`.

Once that's done, you have to open a terminal in the directory where you
extracted the bot files and run `python main.py` once. The output will tell you
that your configuration file is incomplete. You will notice that it will have
created an empty configuration file for you. It's called config.json in the
same directory where main.py is.

You can open up the configuration in any text editor, but the notepad.exe that
comes with Windows by default is probably the worst option here. The first
things you have to enter are the username of your bot and an OAuth key for it.
You can either use your own Twitch account or create a new account only for the
bot, but in each case you need a proper Twitch account. Log into that account
and go to https://twitchapps.com/tmi/ to get an OAuth token and paste that into
the "oauth" field in the configuration file.

The last thing you have to enter is the list of channels your bot is supposed
to join. It should look soomething like this:

```JSON
"channels": [
    "yourchannelname"
]
```

Once you're done, save and close the file and run the bot again with
`python main.py` and this time it should work.

## How do commands work?

First of all, there is a command prefix. It's usually an exclamation point (!),
but it can actually be set to something else. The command prefix is how the bot
knows that you're trying to run a command and not just typing a normal message
in chat.

Every command has a name and zero or more parameters. The name is what you
type directly after the command prefix, e.g. `!uptime`. The parameters are
everything that comes after, e.g. `!mycommand ParamA ParamB`. "ParamA" and
"ParamB" would be the first and second parameters respectively in this case.
Parameters are separated by spaces. If you want to pass something that has a
space, surround it by quotes ("), e.g. `!say "Hello chat!"`.

## Plugins that come out-of-the-box

### The General plugin

The General plugin has a few commands that you just expect to be there.

| Command | Description |
| ------- | ----------- |
| help | Reply with a list of available commands. |
| commands | Do the same as help. |
| say | Say something in chat. |
| quit | Leave the chat. |
| alias | Create a custom command. |
| uptime | Reply with the duration of the current stream. |

#### The alias command

The alias command lets you create custom commands for your bot without the need
to learn programming. You can define the new command right in chat.

```
!alias @everyone hello say Hello $u!
```

The above command would create a new command called `!hello`. It's usable by everyone and runs the comand `!say Hello $u`. The `$u` will be replaced with
the name of the user who sent the command, so if I, Buttercak3, would send the
command, the bot would reply with "Hello Buttercak3!".

There are a few more special character sequences other than `$u` that you can use. Every one of them starts with a dollar sign.

| Sequence | Description |
| -------- | ----------- |
| u | The name of the user who sent the message |
| c | The name of the current Twitch channel |
| 1-9 | A parameter that on can pass to the command |

The last one of those requires a bit of explanation. Let's say you wanted to
create a command that does not greet the user that sent the message, but
another user. You'd want it to work like this:

```
Buttercak3: !hello SomeUser morning
Bot: Hello SomeUser! I hope you're having a great morning.
```

For this to work, you have to define the command like this:

```
!alias @everyone hello say Hello $1! I hope you're having a great $2.
```

The `$1` and `$2` will be replaced with the first and second things you type
after the command name respectively.

### The GitHub plugin

> Note: This plugin isn't usable yet. There is no way for it to get an API key
> for GitHub.

This plugin waits for someone to mention a GitHub issue and posts a link to it
in chat.

### The LinkPreview plugin

This plugin waits for someone to post a link in chat and replies with a short
description of what's behind that link.

| Command | Description |
| ------- | ----------- |
| linkpreview | Turn this plugin on or off |

You can also define URLs that should be ignored by this plugin in the
config.json file. There should be a section "LinkPreview" with "ignored_urls". In the same section there should also be "previewLinks". In there, you can define who can have their links previewed.

```JSON
"ignored_urls": [
  "https://www.twitch.tv",
  "https://www.google.com"
],
"linkPreview": [
    "broadcaster",
    "moderator",
    "subscriber"
]
```

### The Stats plugin

This plugin collects statistics about your chat and puts them in a database (SQLite3). It doesn't do much else yet, but you could use it to create a
website with statistics about your most active chatters, most used commands,
and many more things in the future.

### The Strawpoll plugin

This plugin does 2 things:

Its first function is to wait for someone in chat to post a link to a
strawpoll.me poll. It then posts the poll question and all possible answers as
a preview in chat. This is to let people know what a poll is about before they
click the link.

The second function is a command to create a new poll with the `strawpoll`
command. It will then post the link to the newly created poll in chat.

```
!strawpoll "What should we play next?" "Game A" "Game B"
```

Make sure that you always use quotes (") around the question and answers if
they contain spaces.
