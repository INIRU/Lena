# pylint: disable=relative-beyond-top-level

import discord

from ..etc import Utility
from discord.ext import commands


class music_help_command(commands.Cog, name="Music-Help"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="music", aliases=["music-help", "뮤직", "노래"])
    async def _music_help(self, message):
        await Utility.Embed.music_help_embed(self, message)


def setup(bot):
    bot.add_cog(music_help_command(bot))
