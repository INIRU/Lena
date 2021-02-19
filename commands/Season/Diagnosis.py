#pylint: disable=relative-beyond-top-level
#pylint: disable=no-member

import discord
import hcskr
import json
import datetime

from ..etc import Utility
from discord.ext import commands, tasks

class diagnosis_command(commands.Cog, name="Season"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.auto_diagnosis.start()

    @tasks.loop(seconds=30)
    async def auto_diagnosis(self):
        await Utility.Utility.Diagnosis.auto_diagnosis(self)       

    @commands.group(name="자가진단", aliases=["자진"])
    async def _diagnosis(self, message):
        if message.invoked_subcommand is None:
            await message.invoke(self.bot.get_command('도움말'), helpcmd="자가진단")

    @_diagnosis.command(name="지금", aliases=["now"])
    async def _now(self, message):
        await Utility.Utility.Diagnosis.diagnosis(self, message.author.id)

    @_diagnosis.command(name="등록", aliases=["register", "가입"])
    @commands.dm_only()
    async def _register(self, message):
        await Utility.Utility.Diagnosis.register_event(self, message, message.author)
    
    @_diagnosis.command(name="건너뛰기", aliases=["skip", "skp", "jump"])
    async def _skip(self, message):
        bools = await Utility.Utility.Diagnosis.skip_settings(self, message.author)
        await message.author.send(f"{message.author.mention}, 자동자가진단 건너뛰기: **{'활성화' if bools == True else '비활성화'}**")

    @_diagnosis.command(name="탈퇴", aliases=["삭제"])
    async def _withdrawal(self, message):
        await Utility.Utility.Diagnosis.account_withdrawal(self, message)
        await message.author.send(f"{message.author.mention}, 정상적으로 탈퇴처리 되었습니다!")


def setup(bot):
    bot.add_cog(diagnosis_command(bot))
