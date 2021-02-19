# pylint: disable=relative-beyond-top-level

import discord
import json
import typing
import datetime

from discord.ext import commands
from ..etc import Utility


class kick_command(commands.Cog, name="Moderation"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="추방", aliases=["kick", "킥"])
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(kick_members=True)
    async def _kick(self, message, member: discord.Member, *, reason: str = "없음"):
        if not member.bot and not member.guild_permissions.administrator:
            logging_channel = (await Utility.Warnings.moder_get_limit(self, message))["logging_channel"]

            emb = discord.Embed(color=0x1a1919)
            emb.set_author(name=f"Kicked {member}", icon_url=member.avatar_url)
            emb.add_field(name="👮 **처리자:**",
                          value=f"{message.author} **[{message.author.mention}]**", inline=False)
            emb.add_field(name="🙍 **유저:**",
                          value=f"{member} **[{member.mention}]**", inline=False)
            emb.add_field(name="> 📃 __**정보**__",
                          value=f"**• 사유:** {reason}", inline=False)
            emb.timestamp = datetime.datetime.utcnow()
            if logging_channel and message.guild.get_channel(logging_channel) != None:
                await self.bot.get_channel(int(logging_channel)).send(embed=emb)
            else:
                await message.send(embed=emb)
            await member.kick(reason=reason)
        else:
            await message.send(f"{message.author.mention}, 봇이나 관리자 권한을 보유하고있는 유저에게는 **`{message.command.cog_name}`**명령어를 사용할 수 없습니다.")


def setup(bot):
    bot.add_cog(kick_command(bot))
