# pylint: disable=relative-beyond-top-level

import discord
import json
import typing

from ..etc import Utility
from discord.ext import commands


class setwarn_command(commands.Cog, name="Moderation"):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="경고설정", aliases=["setwarn"], case_insensitive=True)
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(ban_members=True)
    async def _setwarn(self, message):
        if message.invoked_subcommand is None:
            await message.invoke(self.bot.get_command('도움말'), helpcmd="경고설정")

    @_setwarn.command(name="한도", aliases=["limit"])
    async def _setlimit(self, message, limit: int):
        if 0 < limit < 26:
            limit = await Utility.Warnings.moder_set_limit(self, message, limit)
            await message.send(f"{message.author.mention}, 경고 한도가 **`{limit[1]}`**회로 변경되었습니다.\n경고 한도 보다 경고 횟수가 많을 경우 경고 부여를 받을시 서버에서 차단됩니다.")
        else:
            await message.send(f"{message.author.mention}, **`1~25`** 사이로 입력하여 주세요.")

    @_setwarn.command(name="채널", aliases=["로그", "channel", "chn"])
    async def _setlogging(self, message, channel: discord.TextChannel):
        channel = await Utility.Warnings.moder_set_channel(self, message, channel)
        await message.send(f"{message.author.mention}, 경고 로그채널이 {(self.bot.get_channel(int(channel))).mention}채널로 변경되었습니다.")


def setup(bot):
    bot.add_cog(setwarn_command(bot))
