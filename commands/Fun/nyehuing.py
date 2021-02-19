# pylint: disable=relative-beyond-top-level

import discord
import typing

from ..etc import Utility
from discord.ext import commands


class nyehuing_command(commands.Cog, name="Fun"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="녜힁", aliases=["nyehuing"])
    async def _nyehuing(self, message, length: typing.Optional[int] = 2):
        if 0 < length <= 7:
            name = Utility.Utility.nyehuing(self, length)
            await message.send(f"{message.author.mention}, **`{name}`**")
        else:
            await message.send(f"{message.author.mention}, **`0~7`**글자 이내로 입력하여 주세요.")


def setup(bot):
    bot.add_cog(nyehuing_command(bot))
