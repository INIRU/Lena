# pylint: disable=relative-beyond-top-level

import discord
import json
import typing
import datetime

from discord.ext import commands
from ..etc import Utility


class warn_command(commands.Cog, name="Moderation"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="경고부여", aliases=["warn"])
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(ban_members=True)
    async def _warn(self, message, member: discord.Member, *, reason: str = "없음"):
        if not member.bot and not member.guild_permissions.administrator:
            warns = await Utility.Warnings.moder_warn(self, message, member, reason)
            warns_limit = (await Utility.Warnings.moder_get_limit(self, message))["limit"]
            logging_channel = (await Utility.Warnings.moder_get_limit(self, message))["logging_channel"]

            if warns < warns_limit:
                emb = discord.Embed(color=0x1a1919)
                emb.set_author(name=f"Warnned {member}",
                               icon_url=member.avatar_url)
                emb.add_field(name="👮 **처리자:**",
                              value=f"{message.author} **[{message.author.mention}]**", inline=False)
                emb.add_field(
                    name="🙍 **유저:**", value=f"{member} **[{member.mention}]**", inline=False)
                emb.add_field(name="> 📃 __**정보**__",
                              value=f"**• 사유:** {reason}\n**• 경고 개수:** **{warns}** / **{warns_limit}**\n**• 처벌:** 경고 `{warns_limit}`회 누적 시 서버에서 차단됩니다.", inline=False)
                emb.timestamp = datetime.datetime.utcnow()
                if logging_channel and message.guild.get_channel(logging_channel) != None:
                    await self.bot.get_channel(int(logging_channel)).send(embed=emb)
                else:
                    await message.send(embed=emb)

            elif warns >= warns_limit:
                await message.invoke(self.bot.get_command('ban'), member=member, reason=f"경고 `{warns_limit}`회 누적으로 서버에서 차단되었습니다.")
        else:
            await message.send(f"{message.author.mention}, 봇이나 관리자 권한을 보유하고있는 유저에게는 **`{message.command.cog_name}`**명령어를 사용할 수 없습니다.")


def setup(bot):
    bot.add_cog(warn_command(bot))
