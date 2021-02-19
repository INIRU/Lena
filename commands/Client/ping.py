import discord
import json

from discord.ext import commands

with open("./data/bot_config.json", "r", encoding="UTF-8") as f:
    data = json.load(f)
Pong = data["LenaClient"]["emoji"]["Pong"]


class ping_command(commands.Cog, name="Client"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="핑", aliases=["ping"])
    async def _ping(self, message):
        await message.send(f"{message.author.mention}, {Pong} Pong! `{self.bot.latency*1000:,.0f}ms`")


def setup(bot):
    bot.add_cog(ping_command(bot))
