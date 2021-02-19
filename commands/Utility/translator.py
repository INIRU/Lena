# pylint: disable=unused-variable

import discord
import requests
import asyncio
import urllib.request
import json

from discord.ext import commands

client_id = "VUBIC4VZx9ceUjvHpHrZ"
client_secret = "MpLn_ctMk3"
with open('./data/bot_config.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
Lenaimg = data["LenaClient"]["emoji"]["Lenaimg"]


class translator_command(commands.Cog, name="Utility"):
    def __init__(self, bot):
        self.bot = bot

    def lang_api(self, text):
        encQuery = urllib.parse.quote(text)
        data = "query=" + encQuery
        url = "https://openapi.naver.com/v1/papago/detectLangs"
        request = urllib.request.Request(url)
        request.add_header("X-Naver-Client-Id", client_id)
        request.add_header("X-Naver-Client-Secret", client_secret)
        response = urllib.request.urlopen(request, data=data.encode("utf-8"))
        rescode = response.getcode()
        if(rescode == 200):
            response_body = json.loads(response.read())
            return response_body['langCode']
        else:
            return "언어감지불가"

    @commands.command(name="번역", aliases=["파파고", "papago", "translator", "trans", "번역기"])
    @commands.guild_only()
    async def _translator(self, message, *, text: str):
        language = self.lang_api(text)
        if language == "언어감지불가":
            return await message.send(f"{message.author.mention}, 언어를 감지하지 못했습니다.")
        else:
            with open('./data/translator.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            try:
                langemoji = data[language]['emoji']
                langname = data[language]['kr']
            except:
                return await message.send(f"{message.author.mention}, 지원되지않는 언어입니다.")
            trans = ''
            for lang in data[language]['trans']:
                trans += f"{data[lang]['emoji']}**:** {data[lang]['def']}\n"
            emb = discord.Embed(title=f'{Lenaimg}번역기', color=0x018f3b)
            emb.add_field(name=f"{langemoji}{langname}",
                          value=text, inline=True)
            emb.add_field(name="⇄", value="\u200b", inline=True)
            emb.add_field(name="> 번역가능한 언어", value=trans, inline=True)
            transmsg = await message.send(embed=emb)
            for lang in data[language]['trans']:
                await transmsg.add_reaction(data[lang]['emoji'])

            def check(reaction, user):
                if reaction.message.id != transmsg.id:
                    return False
                return user == message.author
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
            except asyncio.TimeoutError:
                return False

            request_url = "https://openapi.naver.com/v1/papago/n2mt"
            headers = {"X-Naver-Client-Id": "VUBIC4VZx9ceUjvHpHrZ",
                       "X-Naver-Client-Secret": "MpLn_ctMk3"}
            if str(reaction.emoji) == "🇰🇷":
                lang = "ko"
                params = {"source": language, "target": lang, "text": text}
                r = requests.post(
                    request_url, headers=headers, data=params).json()
                tm = r['message']['result']['translatedText']
            elif str(reaction.emoji) == '🇯🇵':
                lang = "ja"
                params = {"source": language, "target": lang, "text": text}
                r = requests.post(
                    request_url, headers=headers, data=params).json()
                tm = r['message']['result']['translatedText']
            elif str(reaction.emoji) == '🇺🇸':
                lang = "en"
                params = {"source": language, "target": lang, "text": text}
                r = requests.post(
                    request_url, headers=headers, data=params).json()
                tm = r['message']['result']['translatedText']
            elif str(reaction.emoji) == '🇮🇹':
                lang = "it"
                params = {"source": language, "target": lang, "text": text}
                r = requests.post(
                    request_url, headers=headers, data=params).json()
                tm = r['message']['result']['translatedText']
            elif str(reaction.emoji) == '🇷🇺':
                lang = "ru"
                params = {"source": language, "target": lang, "text": text}
                r = requests.post(
                    request_url, headers=headers, data=params).json()
                tm = r['message']['result']['translatedText']
            elif str(reaction.emoji) == '🇨🇳':
                lang = "zh-CN"
                params = {"source": language, "target": lang, "text": text}
                r = requests.post(
                    request_url, headers=headers, data=params).json()
                tm = r['message']['result']['translatedText']
            else:
                return False

            await transmsg.clear_reactions()
            emb = discord.Embed(title=f'{Lenaimg}번역기', color=0x018f3b)
            emb.add_field(name=f"{langemoji}{langname}",
                          value=text, inline=True)
            emb.add_field(name="⇄", value="\u200b", inline=True)
            emb.add_field(name=f"{data[lang]['emoji']}{data[lang]['kr']}",
                          value=tm, inline=True)
            emb.set_footer(text=f"PAPAGO API",
                           icon_url="https://i.imgur.com/vp8V7uc.png")
            await transmsg.edit(embed=emb)


def setup(bot):
    bot.add_cog(translator_command(bot))
