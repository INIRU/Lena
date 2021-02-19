# pylint: disable=relative-beyond-top-level

import discord
import json
import requests
import datetime
import typing

from ..etc import Utility
from discord.ext import commands

with open('./data/carriers.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
with open("./data/bot_config.json", "r", encoding="UTF-8") as f:
    imgdata = json.load(f)
Lenaimg = imgdata["LenaClient"]["emoji"]["Lenaimg"]


class carriers_command(commands.Cog, name="Utility"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="배송조회", aliases=["택배", "배송", "배조"])
    async def _carriers(self, message, courier: str, *, bill: typing.Optional[int]):
        item_name = Utility.Utility.item_name(self, courier, bill)
        if courier in data['main']:
            courier_id = data['main'][courier]
            url = f"https://apis.tracker.delivery/carriers/{courier_id}/tracks/{bill}"
            header = {"content-type": "application/json;charset=UTF-8"}
            r = requests.get(url, headers=header)
            if r.status_code == 200:
                rj = r.json()
                C_Form = rj['from']['name'].replace("*", "○")
                C_To = rj['to']['name'].replace("*", "○")
                C_Carriers = rj['carrier']['name']
                C_State = rj['state']['text']
                emb = discord.Embed(title=f"{Lenaimg}배송조회", description=f"""
                **상품:** **`{item_name}`**
                **택배사:** **`{C_Carriers}`**
                **발송인/착수인:** **`{C_Form} => {C_To}`**
                **현재 상태:** **`{C_State}`**
                """, color=0x1b0101, timestamp=datetime.datetime.utcnow())

                info = ""
                past_time = None
                list_json = []
                for i in rj['progresses']:
                    status = i['status']['text']
                    location = i['location']['name'].replace(
                        " ", "").replace("\n", "").replace("\t", "")
                    timestamp = (i['time'][:+10]).replace("-", "")
                    description = i['description']
                    time = (i['time'][+11:-9])
                    if status in ["이동중", "배송출발", "배송중", "상품이동중"]:
                        status_emoji = "🚚"
                    elif status in ["상품인수"]:
                        status_emoji = "📦"
                    elif status in ["배송완료", "배달완료"]:
                        status_emoji = "✅"
                    if past_time == timestamp or past_time == None:
                        info += f"{status_emoji} {status} - **[{location}] {time}** - {description}\n"
                        past_time = timestamp
                    else:
                        list_json.append({"title": past_time, "value": info})
                        info = ""
                        past_time = None
                        info += f"{status_emoji} {status} - **[{location}] {time}** - {description}\n"
                list_json.append({"title": past_time, "value": info})
                list_json = sorted(
                    list_json, key=lambda item: item.get("title"))
                for j in list_json:
                    time = (datetime.datetime.strptime(
                        j['title'], "%Y%m%d")).strftime("%Y - %m - %d")
                    emb.add_field(name=time,
                                  value=j['value'], inline=False)
                emb.set_footer(text=f"{message.author}",
                               icon_url=message.author.avatar_url)
                await message.send(embed=emb)
            else:
                await message.send(f"{message.author.mention}, 운송장 정보를 찾을수 없습니다.")
        else:
            await message.send(f"{message.author.mention}, **`API`**가 지원하는 않는 택배사 입니다.")


def setup(bot):
    bot.add_cog(carriers_command(bot))
