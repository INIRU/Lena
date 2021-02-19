# pylint: disable=relative-beyond-top-level

import discord
import os
import json

from ..etc import Utility
from discord.ext import commands

with open("./data/bot_config.json", "r", encoding="UTF-8") as f:
    data = json.load(f)
Lenaimg = data["LenaClient"]["emoji"]["Lenaimg"]


class shard_info_command(commands.Cog, name="Client"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="샤드정보", aliases=["shardinfo"])
    async def _shard_info(self, message):
        emb = Utility.Embed.shard_info_embed(self)
        await message.send(embed=emb)


def setup(bot):
    bot.add_cog(shard_info_command(bot))
