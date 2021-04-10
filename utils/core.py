import discord
from discord.ext import commands
import asyncio




###############################################################################
# Classes and Constants
###############################################################################



class DiscordClient:
    '''a class to represent a bot instance
    Attributes
    ----------
        client: discord.Client
            the bot client
        config: Config
            the configuration
    Methods
    -------
        _buffer_emoji
            load string representations of an emoji to be used in discord messages
        get_emoji
            get an emoji by name
    '''

    def __init__(self):
        intents = discord.Intents(messages=True, members=True, guilds=True,
            emojis=True, reactions=True)
        from utils.config import Config, CONFIG_PATH
        self.config = Config()
        # load config from json-file
        self.config.from_json(CONFIG_PATH)
        self.client = commands.Bot(command_prefix=",", intents=intents,
                                   loop=asyncio.get_event_loop(), case_insensitive=True)


    def _buffer_emoji(self):
        '''load string representations of an emoji to be used in discord messages
        '''
        from utils.config import CONFIG_PATH
        self.config.from_json(CONFIG_PATH)
        cfg = self.config.emoji.__dict__
        for emoji in cfg:
            cfg[emoji] = str(self.client.get_emoji(cfg[emoji]))
        self.config.emoji.__dict__ = cfg


    def get_emoji(self, name: str) -> str:
        '''get an emoji by name
        '''

        emoji = self.config.emoji.get(name)
        if not emoji:
            self._buffer_emoji()
            emoji = self.config.emoji.get(name)
        return str(emoji)





###############################################################################
# Provide ready instances for importing
###############################################################################

bot = DiscordClient()

