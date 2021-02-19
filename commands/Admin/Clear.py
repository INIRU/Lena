#pylint: disable=relative-beyond-top-level

import discord
import datetime

from ..etc import CmdError
from discord.ext import commands


class clear_command(commands.Cog, name="Admin"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="청소", aliases=["chatclear", "cc"])
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def _clear(self, message, cc: int):
        if 0 < cc < 100:
            messages = await message.channel.purge(limit=cc)
            data = {
                "user": [],
                "bot": []
            }
            for del_msg in messages:
                if not del_msg.author.bot:
                    data["user"].append(del_msg)
                elif del_msg.author.bot:
                    data["bot"].append(del_msg)
            emb = discord.Embed(
                color=self.bot.__color__,
                timestamp=datetime.datetime.utcnow(),
                description=f"총 **{len(messages)}**개의 메세지를 삭제하였습니다.\n"
                "> 삭제된 메세지 통계:\n"
                f"**봇 메세지:** {len(data['bot'])}\n"
                f"**유저 메세지:** {len(data['user'])}\n"
            ).set_author(name="Chat Cleared", icon_url=message.author.avatar_url)
            await message.send(content=f"{message.author.mention}", embed=emb)
            return emb
        else:
            raise CmdError.Client.Int_limited_Error("0,100")


def setup(bot):
    bot.add_cog(clear_command(bot))
