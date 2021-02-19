import discord

from discord.ext import commands


class eval_command(commands.Cog, name="Dev"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.load_extension("jishaku")

    def cog_unload(self):
        self.bot.unload_extension("jishaku")

def setup(bot):
    bot.add_cog(eval_command(bot))