import asyncio
import os
import uuid
from discord import Member, Status, Activity, ActivityType
from discord.ext import commands


# Constants (coming from env variables)
BOT_TOKEN = os.environ['CHAT_BOT_SECRET']                           # REQUIRED
VOICE_CHANNEL_CAT = os.environ['CHAT_VOICE_CAT']                    # REQUIRED

NUM_PARTICIPANTS = int(os.environ.get('CHAT_NUM_PARTICIPANTS', 5))  # OPTIONAL
CHANNEL_ID = int(os.environ.get('CHAT_CHANNEL_ID', None))           # OPTIONAL
HELP_MSG_DELAY = int(os.environ.get('CHAT_HELP_DELAY', 600))        # OPTIONAL
CAN_CREATE_CHANNELS = 'CHAT_CREATE_CHANNELS' in os.environ

# Configuration constants
HELP_MSG = '''Welcome to the social channel!
Please use $play to chat with some complete strangers. It will be a lot of fun!
'''


def are_we_allowed_to_chat(ctx, channel_id=CHANNEL_ID):
    """Return True if we are allowed to chat in a given channel."""
    return channel_id is None or channel_id == ctx.channel.id


class ChatCog(commands.Cog):
    def __init__(self, bot,
                 channel_id=CHANNEL_ID,
                 voice_cat=VOICE_CHANNEL_CAT,
                 help_msg=HELP_MSG,
                 help_msg_delay=HELP_MSG_DELAY):
        self.bot = bot
        self.channel_id = channel_id
        self.voice_cat = None
        self.voice_cat_name = voice_cat
        self.help_msg = help_msg
        self.help_msg_every = help_msg_delay

        self._waiting = set()
        self._chatting = set()
        self._last_help_msg = None
        self._voice_chs = []

    async def get_voice_channels(self, guild):
        """
        Get all voice channels under the `self.voice_cat_name` category.

        Retrun
            List[VoiceChannel]: if the category exists
            None: if the category does not exist.
        """
        # Get the list of voice channels and all folks in them.
        for cat, chs in guild.by_category():
            if cat.name == self.voice_cat_name:
                self.voice_cat = cat

                return chs
        return

    async def create_voice_channel(self, guild):
        return await guild.create_voice_channel(
            str(uuid.uuid1()),
            category=self.voice_cat,
            user_limit=NUM_PARTICIPANTS
        )

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Called automatically when the bot receves a 'ready' event. It can be
        called more than once!
        """
        await self.bot.change_presence(
            status=Status.online,
            activity=Activity(type=ActivityType.listening, name='$help')
        )
        print('Bot is ready')

    @commands.command(help='Chat with random people from the conference')
    async def play(self, ctx, *, member: Member = None):
        """
        Main idea: create a number of voice chat channels under the same
        category. Limit the number of participants per channel to
        NUM_PARTICIPANTS. As soon as people invoke this command, put them in
        the first channel that has a slot available. If no channels with any
        free slot are available, create a new one.

        Ideally the channels are invite only.
        """
        member = member or ctx.author

        self._voice_chs = await self.get_voice_channels(ctx.guild)
        if self._voice_chs is None:
            # The voice channel category does not exist!
            print(f'Please (re)create the {self.voice_cat_name} category')
            await member.send(f'Hello {member.name}, we are having problems ' +
                              'with the social chat. Please contact @loc')
            return

        available = []
        for ch, members in [(ch, ch.members) for ch in self._voice_chs]:
            if len(members) < NUM_PARTICIPANTS:
                available.append(ch)

            if member in members:
                await member.send(
                    f'Hello {member.name}, it looks like you are already ' +
                    f'chatting in channel {ch.name}.'
                )
                return

        if not available and CAN_CREATE_CHANNELS:
            # Need to create more channels!
            try:
                ch = await self.create_voice_channel(ctx.guild)
            except Exception as e:
                print(f'Unable to create new voice channel: {e!r}')
                await member.send('All channels are full. ' +
                                  'Please try again later')
                return
            else:
                self._voice_chs.append(ch)
        elif available:
            ch = available[0]
        else:
            await member.send('All channels are full. Please try again later')
            return

        invite = await ch.create_invite(max_uses=1)
        await member.send(f'Hello {member.name}, follow this invite to ' +
                          'start chatting: ' + invite.url)

    async def resend_help(self):
        await self.bot.wait_until_ready()

        ch = self.bot.get_channel(self.channel_id)
        while True:
            messages = await ch.history(after=self._last_help_msg).flatten()
            if len(messages) >= self.help_msg_every:
                self._last_help_msg = await ch.send(self.help_msg)
            await asyncio.sleep(self.help_msg_every)


if __name__ == '__main__':
    bot = commands.Bot(command_prefix='$')
    bot.add_check(are_we_allowed_to_chat, call_once=False)

    cog = ChatCog(bot, channel_id=CHANNEL_ID)
    bot.add_cog(cog)

    bot.loop.create_task(cog.resend_help())
    bot.run(BOT_TOKEN)
