import discord
from discord.ext import commands


class support_command(commands.Cog, name="Client"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="서포트", aliases=["support"])
    async def _support(self, message):
        await message.send(f"{message.author.mention}, 명령어 사용에 도움이 필요하신가요?\n**https://discord.gg/cGM4PcHvQq (Support Server)**를 방문해주세요!")


def setup(bot):
    bot.add_cog(support_command(bot))
