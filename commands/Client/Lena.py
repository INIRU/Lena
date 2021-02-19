# pylint: disable=relative-beyond-top-level

import discord
import datetime
import json
import koreanbots

from ..etc import Utility
from discord.ext import commands


class lena_command(commands.Cog, name="Client"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="레나", aliases=["lena", "botinfo"])
    async def _lena(self, message):
        await Utility.Embed.lena_info_embed(self, message)


def setup(bot):
    bot.add_cog(lena_command(bot))
