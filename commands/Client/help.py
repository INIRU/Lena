# pylint: disable=relative-beyond-top-level

import discord

from ..etc import Utility
from discord.ext import commands


class help_command(commands.Cog, name="Client"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="도움말", aliases=["도움", "help"])
    async def _help(self, message, *, helpcmd: str = None):
        if not helpcmd:
            await Utility.Embed.help_embed(self, message)
        elif helpcmd:
            await Utility.Utility.Client.command_help(self, message, helpcmd)


def setup(bot):
    bot.add_cog(help_command(bot))
