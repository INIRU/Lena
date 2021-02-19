import discord
import requests
import datetime
import json

from discord.ext import commands

with open('./data/bot_config.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
Lenaimg = data["LenaClient"]["emoji"]["Lenaimg"]


class animation_command(commands.Cog, name="Utility"):
    def __init__(self, bot):
        self.bot = bot

    def days(self, text, year, month, day):
        if text == "int":
            r = ['1', '2', '3', '4', '5', '6', '0']
        if text == "str":
            r = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
        if text == "color":
            r = [0xdbdbdb, 0xffae00, 0x00ceff,
                 0x2fb364, 0x1d1d1d, 0x795305, 0xff0e43]
        aday = datetime.date(year, month, day)
        bday = aday.weekday()
        return r[bday]

    @commands.command(name="애니편성표", aliases=["애편표", "anime"])
    async def animation(self, message):
        y = datetime.datetime.today().year
        m = datetime.datetime.today().month
        d = datetime.datetime.today().day
        now = datetime.datetime.now()
        ymd = now.strftime("%Y%m%d")
        url = "https://www.anissia.net/anitime/list?w=" + \
            (self.days("int", y, m, d))
        r = requests.post(url).json()
        Aname = ''
        Atime = ''
        Ainfo = ''
        for anime in r:
            Animename = anime['s']
            Animebool = anime['a']
            Animesdfull = anime['sd']
            Animelink = anime['l'].replace(" ", "")
            Animeed = anime['ed']
            Animestart = Animesdfull[4:7] + ":" + Animesdfull[7:]
            Animeinfo = anime['g']
            Animetimefull = anime['t']
            Animetime = Animetimefull[0:2] + ":" + Animetimefull[2:]
            if Animebool == True:
                if ymd <= Animesdfull:
                    Aname += f"**|** **[{Animestart}][{Animename}]({Animelink})**\n"
                if ymd > Animesdfull:
                    if int(ymd) >= int(Animeed) > 00000000:
                        Aname += f"**|** **[完][{Animename}]({Animelink})**\n"
                    else:
                        Aname += f"**|** **[{Animename}]({Animelink})**\n"
            elif Animebool == False:
                Aname += f"**[결방][{Animename}]({Animelink})**\n"
            Ainfo += f"**|** **{Animeinfo}**\n"
            Atime += f"**{Animetime}**\n"

        if anime:
            emb = discord.Embed(title="애니편성표", colour=(
                self.days("color", y, m, d)))
            emb.add_field(name=f"\u200b", value=f"{Atime}", inline=True)
            emb.add_field(name=f"> {Lenaimg} **애니이름**",
                          value=f"{Aname}", inline=True)
            emb.add_field(name=f"> ☝ **장르**", value=f"{Ainfo}", inline=True)
            emb.set_footer(text=f"Anissia API | {self.days('str', y, m, d)}")
            await message.send(embed=emb)
        else:
            await message.send(f"{message.author.mention}, 오늘 방영하는 애니가 없습니다.")


def setup(bot):
    bot.add_cog(animation_command(bot))
