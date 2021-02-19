# pylint: disable=relative-beyond-top-level

import discord
import json
import asyncio
import datetime

from ..etc import CmdError, Utility
from discord.ext import commands


class notification_command(commands.Cog, name="Client"):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="알림", aliases=["봇공지", "봇알림", "notification"], case_insensitive=True)
    @commands.bot_has_permissions(manage_messages=True)
    @commands.guild_only()
    async def _notification(self, message):
        if message.invoked_subcommand is None:
            now = datetime.datetime.now()
            with open('./data/bot_config.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            if len(data['LenaClient']['notice']['notification']) == 0:
                raise CmdError.Client.Not_Notification
            emb = discord.Embed(title="📢 알림", color=0x1ab102)
            notification = sorted(
                data['LenaClient']['notice']['notification'], key=lambda item: item.get("datetime"), reverse=True)
            for i, notif in enumerate(notification):
                new = ""
                if int(now.strftime("%Y%m%d")) == notif["datetime"]:
                    new = data["LenaClient"]["emoji"]["new"]
                emb.add_field(name=f"> {notif['name']}{new}", value=(
                    notif['value'].replace(">", "").replace(
                        "\n", "").replace("`", "").replace("*", "")
                    if len(notif['value'].replace(">", "").replace("\n", "").replace("`", "").replace("*", "")) < 17 else notif['value'][0:17].replace(">", "").replace(
                        "\n", "").replace("`", "").replace("*", "") + "..."), inline=False)
            emb.set_footer(text="아래에 있는 이모지를 반응하여 펼쳐보기를 사용할수 있습니다.")
            notifmsg = await message.send(embed=emb)
            for emoji in list(data['LenaClient']['notice']['init'].keys())[:min(len(notification), len(notification))]:
                await notifmsg.add_reaction(emoji)

            def check(reaction, user):
                if reaction.message.id != notifmsg.id:
                    return False
                return user == message.author

            while True:
                try:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
                except asyncio.TimeoutError:
                    return False

                if str(reaction.emoji):
                    if data['LenaClient']['notice']['init'][str(reaction.emoji)] <= i:
                        await notifmsg.clear_reactions()
                        embn = discord.Embed(
                            title=f"📢 {notification[data['LenaClient']['notice']['init'][str(reaction.emoji)]]['name']}", color=0x1ab102)
                        embn.description = notification[data['LenaClient']['notice']['init'][str(
                            reaction.emoji)]]['value']
                        embn.set_footer(text=self.bot.get_user(
                            notification[data['LenaClient']['notice']['init'][str(reaction.emoji)]]['admin']), icon_url=self.bot.get_user(
                            notification[data['LenaClient']['notice']['init'][str(reaction.emoji)]]['admin']).avatar_url)
                        await notifmsg.edit(embed=embn)
                        break
                    else:
                        await notifmsg.remove_reaction(reaction.emoji, user)

    @_notification.command(name="작성", aliases=["add", "추가"])
    @commands.is_owner()
    async def _notification_add(self, message):
        with open('./data/bot_config.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        text = f"{message.author.mention}, 알림의 제목을 작성하여주세요.\n작성을 완료하였다면 `완료` 아니라면 `취소`를 입력하주세요."
        emb = discord.Embed(color=self.bot.__color__, title="📢 알림제목")
        emb.description = "알림 할말"
        exmp = await message.send(embed=emb, content=text)

        def check(msg):
            return msg.author == message.author and msg.channel == message.channel

        while True:
            try:
                msg = await self.bot.wait_for("message", timeout=600, check=check)
            except asyncio.TimeoutError:
                break

            await msg.delete()
            if str(msg.content) != "완료" and str(msg.content) != "취소":
                waittitle = str(msg.content)
                emb.title = f"📢 {str(msg.content)}"
                await exmp.edit(embed=emb)

            elif str(msg.content) == "완료":
                if waittitle:
                    title = waittitle
                    await exmp.edit(content=f"{message.author.mention}, 알림의 할말을 작성하여주세요.\n작성을 완료하였다면 `완료` 아니라면 `취소`를 입력하주세요.")
                    break
                else:
                    await message.send(f"{message.author.mention}, 알림의 제목을 작성하여주세요.")

            elif str(msg.content) == "취소":
                return await exmp.edit(content=f"{message.author.mention}, 알림 작성이 취소되었습니다.", embed=None)

        if title:
            while True:
                try:
                    msg = await self.bot.wait_for("message", timeout=600, check=check)
                except asyncio.TimeoutError:
                    break

                await msg.delete()

                if str(msg.content) != "완료" and str(msg.content) != "취소":
                    waittitle = str(msg.content)
                    emb.description = str(msg.content)
                    await exmp.edit(embed=emb)

                elif str(msg.content) == "완료":
                    if waittitle:
                        value = waittitle
                        await exmp.edit(content=f"{message.author.mention}, 알림의 할말을 작성하여주세요.\n작성을 완료하였다면 `완료` 아니라면 `취소`를 입력하주세요.")
                        break
                    else:
                        await message.send(f"{message.author.mention}, 알림의 제목을 작성하여주세요.")

                elif str(msg.content) == "취소":
                    return await exmp.edit(content=f"{message.author.mention}, 알림 작성이 취소되었습니다.", embed=None)

        if title and value:
            await exmp.edit(content=f"{message.author.mention}, 알림 작성이 완료되었습니다.", embed=None)
            now = datetime.datetime.now()
            data['LenaClient']['notice']['notification'].append(
                {
                    "name": title,
                    "value": value,
                    "admin": message.author.id,
                    "datetime": int(now.strftime("%Y%m%d"))
                }
            )
            if len(data['LenaClient']['notice']) >= 6:
                del data['LenaClient']['notice'][0]

            with open('./data/bot_config.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)

    @_notification.command(name="제거", aliases=["del", "삭제"])
    @commands.is_owner()
    async def _notification_del(self, message):
        with open('./data/bot_config.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        if len(data['LenaClient']['notice']['notification']) == 0:
            raise CmdError.Client.Not_Notification
        emb = discord.Embed(title="📢 알림", color=0x1ab102)
        for i, notif in enumerate(data['LenaClient']['notice']['notification']):
            emb.add_field(name=f"> {notif['name']}", value=(
                notif['value'].replace(">", "").replace(
                    "\n", "").replace("`", "").replace("*", "")
                if len(notif['value'].replace(">", "").replace("\n", "").replace("`", "").replace("*", "")) < 17 else notif['value'][0:17].replace(">", "").replace(
                    "\n", "").replace("`", "").replace("*", "") + "..."), inline=False)
            emb.set_footer(text="아래에 있는 이모지를 반응하여 펼쳐보기를 사용할수 있습니다.")
        notifmsg = await message.send(embed=emb)

        for emoji in list(data['LenaClient']['notice']['init'].keys())[:min(len(data['LenaClient']['notice']['notification']), len(data['LenaClient']['notice']['notification']))]:
            await notifmsg.add_reaction(emoji)

        def check(reaction, user):
            if reaction.message.id != notifmsg.id:
                return False
            return user == message.author

        while True:
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
            except asyncio.TimeoutError:
                return False

            if str(reaction.emoji):
                if data['LenaClient']['notice']['init'][str(reaction.emoji)] - 1 <= i:
                    await notifmsg.clear_reactions()
                    title = data['LenaClient']['notice']['notification'][data['LenaClient']
                                                                         ['notice']['init'][str(reaction.emoji)]]['name']
                    del data['LenaClient']['notice']['notification'][data['LenaClient']
                                                                     ['notice']['init'][str(reaction.emoji)]]
                    break
                else:
                    await notifmsg.remove_reaction(reaction.emoji, user)

        with open('./data/bot_config.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        await notifmsg.edit(embed=None, content=f"{message.author.mention}, **`{title}`**알림을 삭제하였습니다.")


def setup(bot):
    bot.add_cog(notification_command(bot))
