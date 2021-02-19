# pylint: disable=no-member
# pylint: disable=relative-beyond-top-level

import discord
import json
import uuid
import requests
import koreanbots
import datetime
import logging
import traceback

from discord.ext import commands, tasks
from colorama import init, Fore, Back, Style
from ..etc import CmdError, Utility

init(autoreset=True)

with open('./data/bot_config.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
Lenaimg = data["LenaClient"]["emoji"]["Lenaimg"]
Errorimg = data["LenaClient"]["emoji"]["Error"]
Helpimg = data["LenaClient"]["emoji"]["Help"]
Iniruimg = data["LenaClient"]["emoji"]["iniru"]
redcolor = Fore.RED + Style.BRIGHT
userdata = {}


class setup_client(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.change_status.start()
        self.kr_bot = koreanbots.Client(
            self.bot, data["LenaClient"]["koreanbot_token"])
        self.koreanbot_heart.start()

    @tasks.loop(minutes=5)
    async def koreanbot_heart(self):
        with open('./data/bot_config.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        Heart = (await self.kr_bot.getBot('686606116314152994')).votes
        data['LenaClient']['heart'] = Heart
        with open('./data/bot_config.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    @tasks.loop(seconds=1)
    async def change_status(self):
        await self.bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching, name=f"e!도움말/{len(self.bot.guilds)}서버/{len(self.bot.users)}유저")
        )

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        with open('./data/Moder_log.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        if str(guild.id) in data:
            del data[str(guild.id)]
        with open('./data/Moder_log.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    @commands.Cog.listener()
    async def on_command(self, message):
        Utility.LenaCleint_logger.command_logger.info(
            f"{message.author}: {message.command}")
        BASEURL = "https://api.koreanbots.dev"
        r = requests.get(
            f'{BASEURL}/bots/voted/{message.author.id}', headers={"token": data["LenaClient"]["koreanbot_token"]})
        rj = r.json()
        if r.status_code in [200, 404]:
            emb = discord.Embed(
                title=f"{Iniruimg} 하트", color=self.bot.__color__)
            emb.description = "레나봇은 ❤로 제작된 봇입니다.\n여러분이 ❤를 눌러주실때마다 레나봇에게 큰 도움이 됩니다!\n**[클릭](https://koreanbots.dev/bots/686606116314152994)**"
            emb.set_footer(text="이 알림은 레나봇이 리붓되거나 24시간 뒤에 다시 알려드립니다.")
            if "message" in rj or rj['voted'] == False:
                now = datetime.datetime.now()
                if str(message.author.id) in userdata and userdata[str(message.author.id)] != now.strftime("%Y%m%d"):
                    userdata[str(message.author.id)] = now.strftime("%Y%m%d")
                    await message.send(embed=emb)
                elif str(message.author.id) not in userdata:
                    userdata[str(message.author.id)] = now.strftime("%Y%m%d")
                    await message.send(embed=emb)

    @commands.Cog.listener()
    async def on_command_error(self, message, error):
        if isinstance(error, commands.CommandNotFound):
            return

        elif isinstance(error, CmdError.Music.Empty_Queue):
            return await message.send(f"{message.author.mention}, **`{message.command}`**는/(은) 재생목록이 비어있어서 사용할 수 없습니다.")

        elif isinstance(error, CmdError.Music.NoPreviousTracks):
            return await message.send(f"{message.author.mention}, **`이전곡`**이 없습니다.")

        elif isinstance(error, CmdError.Music.NoMoreTracks):
            return await message.send(f"{message.author.mention}, **`다음곡`**이 없습니다.")

        elif isinstance(error, CmdError.Music.AlreadyConnectedToChannel):
            return await message.send(f"{message.author.mention},  이미 <#{error}>채널에 접속해 있습니다.")

        elif isinstance(error, CmdError.Music.Not_playing):
            return await message.send(f"{message.author.mention}, **`{message.command}`**는/(은) 노래를 재생하고 사용하여 주세요.")

        elif isinstance(error, CmdError.Music.PlayerIsAlreadyPaused):
            return await message.send(f"{message.author.mention}, 이미 일시정지된 상태입니다.")

        elif isinstance(error, CmdError.Music.PlayerIsAlreadyResumed):
            return await message.send(f"{message.author.mention}, 이미 재개된 상태입니다.")

        elif isinstance(error, CmdError.Music.Not_Seek_Live):
            return await message.send(f"{message.author.mention}, **`{message.command}`**는/(은) 라이브 트랙에 사용할 수 없습니다.")

        elif isinstance(error, CmdError.Music.TrackNotfound):
            return await message.send(f"{message.author.mention}, 트랙을 찾을수 없습니다.")

        elif isinstance(error, CmdError.Music.NoVoiceChannel):
            return await message.send(f"{message.author.mention}, **`{message.command}`**는/(은) 음성채널에 접속후 사용해주세요.")

        elif isinstance(error, CmdError.Music.Not_Requster):
            return await message.send(f"{message.author.mention}, **`{message.command}`**는/(은) 노래를 요청한 사람 또는 **`관리자*`**가 사용할 수 있습니다.")

        elif isinstance(error, CmdError.Moder.FaileUnwarn):
            return await message.send(f"{message.author.mention}, 차감할 경고수가 없습니다.")

        elif isinstance(error, CmdError.Moder.FaileUnwarn):
            return await message.send(f"{message.author.mention}, 이미 기간벤을 당한 유저입니다.")

        elif isinstance(error, CmdError.Client.Not_Notification):
            return await message.send(f"{message.author.mention}, 알림이 없습니다.")

        elif isinstance(error, CmdError.Client.Not_Commands):
            return await message.send(f"{message.author.mention}, 봇에 없는 **`명령어`**입니다.")

        elif isinstance(error, CmdError.Client.emoji_timeout):
            return await message.send(f"{message.author.mention}, 이모지 반응대기 시간이 초과되었습니다.")

        elif isinstance(error, CmdError.Client.emoji_timeout):
            return await message.send(f"{message.author.mention}, 메세지 입력대기 시간이 초과되었습니다.")

        elif isinstance(error, CmdError.Client.Not_Page):
            return await message.send(f"{message.author.mention}, **{error}**페이지 밖에 없습니다.")

        elif isinstance(error, CmdError.Client.Int_limited_Error):
            error = str(error).split(",")
            return await message.send(f"{message.author.mention}, **`{error[0]}~{error[1]}`** 사이의 숫자만 입력할 수 있습니다.")

        elif isinstance(error, CmdError.Client.Commands_NotHelping):
            return await message.send(f"{message.author.mention}, **`{error}`**명령어의 도움말이 없습니다.")

        elif isinstance(error, CmdError.Season.UserInData):
            return await message.send(f"{message.author.mention}, 이미 **등록**을 하였습니다.\n등록정보를 변경하시려면 탈퇴를 해주세요.")
        
        elif isinstance(error, CmdError.Season.UserNotInData):
            return await message.send(f"{message.author.mention}, 먼저 **등록**을 하신후에 사용하여 주세요.")

        elif isinstance(error, CmdError.Admin.NotLoggingData):
            return await message.send(f"{message.author.mention}, 서버의 **로그 데이터**가 없습니다.")

        elif isinstance(error, commands.NoPrivateMessage):
            return await message.send(f"{message.author.mention}, **`{message.command}`**는/(은) **서버**에서만 사용할 수 있습니다.")

        elif isinstance(error, commands.PrivateMessageOnly):
            return await message.send(f"{message.author.mention}, **`{message.command}`**는/(은) 레나봇**개인DM**에서만 사용할 수 있습니다.")

        elif isinstance(error, commands.NotOwner):
            emb = Utility.Utility.command_missing_perm(
                self, message, ["bot_owner"], bot=message.author.bot)
            return await message.send(embed=emb)

        elif isinstance(error, commands.DisabledCommand):
            return await message.send(f"{message.author.mention}, **`{message.command}`**는/(은) 비활성화 되어있습니다.")

        elif isinstance(error, commands.BadArgument):
            cmd = message.command
            return await Utility.Utility.Client.command_help(self, message, str(cmd), f"{message.author.mention}, 잘못된 요청값이 있습니다.")

        elif isinstance(error, commands.MissingRequiredArgument):
            cmd = message.command
            return await Utility.Utility.Client.command_help(self, message, str(cmd), f"{message.author.mention}, **`{error.param.name}`**필수 항목이 누락되었습니다.")

        elif isinstance(error, (commands.BotMissingPermissions, commands.MissingPermissions)):
            emb = Utility.Utility.command_missing_perm(
                self, message, error.missing_perms, bot=message.author.bot)
            return await message.send(embed=emb)

        elif isinstance(error, commands.CommandOnCooldown):
            return await message.send(f"{message.author.mention}, **`{message.command}`**명령어는 쿨 다운 중입니다.\n**{Utility.Utility.second_convert(self, int('%.0f' % error.retry_after))}**남았습니다.")

        elif isinstance(error, commands.CommandInvokeError):
            trace_channel = await self.bot.fetch_channel(792825312383598633)
            errorid = str(uuid.uuid4())
            await message.send(
                embed=discord.Embed(
                    title=f"{Errorimg} 알 수 없는 오류가 발생했습니다.",
                    description=f"다음 정보를 개발자에게 전달해주시면 문제해결에 큰 도움이 됩니다.\n**UUID:** `{errorid}`\n",
                    color=self.bot.__color__,
                    timestamp = datetime.datetime.now(),
                )
                .set_footer(text=message.author, icon_url=message.author.avatar_url)
            )
            trace_embed = discord.Embed(
                title=f"{Errorimg} 알 수 없는 오류를 발견하였습니다.\n**UUID**: ``{errorid}``",
                color=self.bot.__color__,
                description=f"**Version**: ``{self.bot.__version__}``\n"
                f"**User:** `{message.author}` [`{message.author.id}`]\n"
                f"**Guild:** `{message.author.guild}` [`{message.author.guild.id}`]\n"
                f"**Channel:** `{message.channel}` [`{message.channel.id}`]\n"
                f"**Command:** `{message.command}`\n"
                f"**Bot Permission:** `{message.guild.me.guild_permissions.value}`",
            )
            if not error.__cause__:
                trace_embed.add_field(
                    name="**Traceback:**",
                    value=f"```py\n{''.join(traceback.format_exception(type(error), error, error.__traceback__, limit=3))}\n```",
                )
            else:
                trace_embed.add_field(
                    name="**Traceback:**",
                    value=f"```py\n{''.join(traceback.format_exception(type(error.__cause__), error.__cause__, error.__cause__.__traceback__, limit=3))}\n```",
                )
            trace_embed.timestamp = datetime.datetime.now()
            trace_embed.set_footer(text=message.author, icon_url=message.author.avatar_url)
            return await trace_channel.send(embed=trace_embed)
        else:
            print(error)


def setup(bot):
    bot.add_cog(setup_client(bot))
