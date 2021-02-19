# pylint: disable=relative-beyond-top-level
# pylint: disable=no-member

import discord
import typing
import datetime
import json

from discord.ext import commands, tasks
from ..etc import Utility


class tempban_command(commands.Cog, name="Moderation"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.tempban_unban.start()

    @tasks.loop(seconds=5)
    async def tempban_unban(self):
        with open('./data/Moder_log.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        now = datetime.datetime.now()
        guilds = list(data.keys())
        for g in guilds:
            users = list(data[g]["temp_bans"].keys())
            guild = self.bot.get_guild(int(g))
            for user in users:
                if int(data[g]["temp_bans"][user]) <= int(now.strftime("%Y%m%d%H")):
                    del data[g]["temp_bans"][user]
                    with open('./data/Moder_log.json', 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=4, ensure_ascii=False)
                    unban_user = self.bot.get_user(int(user))
                    try:
                        await guild.unban(unban_user)
                        await unban_user.send(f"{unban_user.mention}, **`{guild.name}`**서버의 기간벤이 해제되었습니다.")
                    except:
                        pass
                    Utility.LenaCleint_logger.moder_logger.debug(
                        f"User TempUnban {self.bot.get_user(int(user))}")

    @commands.command(name="기간벤", aliases=["템프벤", "임시벤", "tempban"])
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(ban_members=True)
    async def _tempban(self, message, member: discord.Member, days: int, *, reason: typing.Optional[str] = "없음"):
        if not member.bot and not member.guild_permissions.administrator:
            time = await Utility.Warnings.moder_tempban(self, message, member, days, f"{reason} + {days}일 벤")
            timed = time.strftime(
                "`%Y. %m. %d` **`%p %I:%M`**").replace('PM', '오후').replace('AM', '오전')
            logging_channel = (await Utility.Warnings.moder_get_limit(self, message))["logging_channel"]

            emb = discord.Embed(color=0x1a1919)
            emb.set_author(
                name=f"TempBanned {member}", icon_url=member.avatar_url)
            emb.add_field(name="👮 **처리자:**",
                          value=f"{message.author} **[{message.author.mention}]**", inline=False)
            emb.add_field(name="🙍 **유저:**",
                          value=f"{member} **[{member.mention}]**", inline=False)
            emb.add_field(name="> 📃 __**정보**__",
                          value=f"**• 사유:** {reason}\n**• 해제일:** {timed}", inline=False)
            emb.timestamp = datetime.datetime.utcnow()
            if logging_channel and message.guild.get_channel(logging_channel) != None:
                await self.bot.get_channel(int(logging_channel)).send(embed=emb)
            else:
                await message.send(embed=emb)
            await member.send(f"{member.mention}, **`{message.guild.name}`**서버에서 기간벤을 당하였습니다.\n**해제일:** {time}")
        else:
            await message.send(f"{message.author.mention}, 봇이나 관리자 권한을 보유하고있는 유저에게는 **`{message.command.cog_name}`**명령어를 사용할 수 없습니다.")


def setup(bot):
    bot.add_cog(tempban_command(bot))
