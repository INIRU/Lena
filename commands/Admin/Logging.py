# pylint: disable=relative-beyond-top-level

import discord
import json
import datetime
import asyncio

from ..etc import Utility
from discord.ext import commands

OPTIONS = {
    "1️⃣": 0,
    "2⃣": 1,
    "3⃣": 2,
    "4⃣": 3,
    "5⃣": 4,
}

class logging_command(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    @commands.guild_only()
    async def on_raw_message_delete(self, payload):
        channel = Utility.Admin.Logger.get_logging_channel(self, payload.guild_id)
        setting = Utility.Admin.Logger.get_logging_setting(self, payload.guild_id, "Deleted")
        if channel is not None and setting:
            if payload.cached_message is not None:
                delelte_message = payload.cached_message
                if delelte_message.author.bot:
                    return

                emb = discord.Embed(
                    title="📜 Message Deleted",
                    color=0x0f0f0f,
                    description="> **메세지**가 삭제되었습니다.\n"
                    f"**작성자:** {delelte_message.author.mention} [`{delelte_message.author.id}`]\n"
                    f"**채널:** {delelte_message.channel.mention} [`{delelte_message.channel.id}`]\n"
                ).set_footer(text=delelte_message.author, icon_url=delelte_message.author.avatar_url)
                if delelte_message.content == "":
                    emb.add_field(name="**내용:**", value="아주 넓고 먼 범위를 찾아봤지만 찾을 수 없었어요ㅠㅠ")
                elif delelte_message.content != "":
                    emb.add_field(name="**내용:**", value=delelte_message.content)
            else:
                emb = discord.Embed(
                    title="📜 Message Deleted",
                    color=0x0f0f0f,
                    description="> **메세지**가 삭제되었습니다.\n"
                ).set_footer(text="Not Cached")
                emb.add_field(name="**내용:**", value="**메세지 캐시**를 찾을 수 없습니다.")
            emb.timestamp = datetime.datetime.utcnow()
            await channel.send(embed=emb)

def setup(bot):
    bot.add_cog(logging_command(bot))