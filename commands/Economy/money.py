# pylint: disable=relative-beyond-top-level

import discord
import json
import datetime

from discord.ext import commands


class money_command(commands.Cog, name="Economy"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="돈", aliases=["내돈", "money", "소지금"])
    async def _money(self, message):
        pass


def setup(bot):
    bot.add_cog(money_command(bot))
