# Random Chat

A Discord bot that splits people up in voice channels for some random chat time


## Intended Use

The main idea here is to have a Discord bot that can be used at social events
(e.g. coffee breaks at an online conference) to foster random conversations and
networking.


## Installation

You need Python 3.6 or later.

Install dependencies with ```pip``` and run the bot:

```
% pip install -r requirements
% BOT_TOKEN=XYZ VOICE_CHANNEL_CAT="your category" python3 ./bot.py
```

You will have to invite the bot to your server and give it the necessary permissions (see below).


## Configuration

The bot can be configured using environment variables. Some are required, some are optional with sane defaults:

### Required
* CHAT\_BOT\_SECRET: your Discord Bot token/secret.
* CHAT\_VOICE\_CAT: the name of the voice channel category on your server. People will be invited to voice channels under this category.

### Optional
* CHAT\_NUM\_PARTICIPANTS: maximum number of participant per voice channel. Defaults to 5. A voice channel with frewer than CHAT\_NUM\_PARTICIPANTS members is considered available.
* CHAT\_CHANNEL\_ID: if defined, the bot will only listen for commands in this channel. Defaults to None (i.e. the bot will listen in all channels).
* CHAT\_HELP\_DELAY: the bot will send its help message every CHAT\_HELP\_DELAY seconds. Defaults to 600 (i.e. 10 minutes).
* CHAT\_CREATE\_CHANNELS: if defined at all, the bot will create channels if none are available.


## Permissions

The bot will need, at a minimum, permission to:

* Listen to messages.
* Send messages to members.
* Create voice channels (if needed, see above).
