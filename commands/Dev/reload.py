# pylint: disable=relative-beyond-top-level

import discord

from ..etc import Utility
from discord.ext import commands


class reload_command(commands.Cog, name="Dev"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="reload", aliases=["리로드"])
    @commands.is_owner()
    async def _reload(self, message):
        await Utility.Utility.reload_cogs(self.bot, message)



def setup(bot):
    bot.add_cog(reload_command(bot))
