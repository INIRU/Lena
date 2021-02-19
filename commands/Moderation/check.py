# pylint: disable=relative-beyond-top-level

import discord
import json
import typing
import datetime

from discord.ext import commands
from ..etc import Utility


with open('./data/bot_config.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
Errorimg = data["LenaClient"]["emoji"]["Error"]


class check_command(commands.Cog, name="Moderation"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="경고확인", aliases=["check", "warncheck"])
    async def _check(self, message, member: typing.Optional[discord.Member] = None):
        if not member:
            member = message.author
        elif member and not message.author.guild_permissions.administrator:
            return await message.send(f"{message.author.mention}, 다른사람의 경고정보를 보려면 `관리자*`권한이 필요합니다.")
        data = await Utility.Warnings.moder_checked(self, message, member)
        warns_limit = (await Utility.Warnings.moder_get_limit(self, message))["limit"]

        emb = discord.Embed(color=0x1a1919)
        emb.set_author(name=f"Cheked {member}", icon_url=member.avatar_url)
        emb.description = f"{member.mention}님의 경고 정보입니다."
        emb.add_field(name=" 📃 __**정보:**__",
                      value=f"**• 경고 개수:** **{data['warns']}** / **{warns_limit}**")
        log = ""
        if len(data["warn_logging"]) >= 1:
            for i in data["warn_logging"]:
                log += f"{'[+]' if i['Type'] == True else '[-]'} 처리자: {self.bot.get_user(i['Moder'])} 사유: {i['Reason']}\n"
            emb.add_field(name="> 📜 __**로그:**__",
                          value=f"```css\n{log}```", inline=False)
        emb.timestamp = datetime.datetime.utcnow()
        await message.send(embed=emb)


def setup(bot):
    bot.add_cog(check_command(bot))
