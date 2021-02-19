# pylint: disable=relative-beyond-top-level

import discord
import json
import datetime

from ..etc import Utility
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType

with open("./data/bot_config.json", "r", encoding="UTF-8") as f:
    data = json.load(f)
coin = data["LenaClient"]["emoji"]["coin"]


class job_event_command(commands.Cog, name="Economy"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="일", aliases=["일하기", "job", "parttime"])
    @commands.cooldown(1, 7200, BucketType.user)
    async def _job_event(self, message):
        await Utility.Economy.job_event(self, message, message.author.id)


def setup(bot):
    bot.add_cog(job_event_command(bot))
