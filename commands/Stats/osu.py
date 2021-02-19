import discord
import requests
import json
import typing
import asyncio

from discord.ext import commands

APIKEY = "89b73e4934fea182157f934aa1f5783eb0d6a19f"
with open("./data/bot_config.json", "r", encoding="UTF-8") as f:
    data = json.load(f)
osust = data["LenaClient"]["emoji"]["osust"]
osumania = data["LenaClient"]["emoji"]["osumania"]
osutaiko = data["LenaClient"]["emoji"]["osutaiko"]
osucatch = data["LenaClient"]["emoji"]["osucatch"]
osurssh = data["LenaClient"]["emoji"]["osurssh"]
osurssh = data["LenaClient"]["emoji"]["osurssh"]
osurss = data["LenaClient"]["emoji"]["osurss"]
osursh = data["LenaClient"]["emoji"]["osursh"]
osurs = data["LenaClient"]["emoji"]["osurs"]
osura = data["LenaClient"]["emoji"]["osura"]


class osu_command(commands.Cog, name="Stats"):
    def __init__(self, bot):
        self.bot = bot

    def stats(self, name, mode):
        url = f"https://osu.ppy.sh/api/get_user?k={APIKEY}&u={name}&m={mode}"
        r = requests.post(url)
        return r.json()

    @commands.command(name="osu", aliases=["오스", "osu!"])
    async def _osu(self, message, name: str, mode: typing.Optional[str]):
        if not mode:
            elist = [osust, osumania, osutaiko, osucatch]
            emb = discord.Embed(title=f"OSU! {name} STATS", description=f"""
            {osust}: **osu!**
            {osumania}: **osu!mania**
            {osutaiko}: **osu!taiko**
            {osucatch}: **osu!catch**
            """, color=0xf87fef)
            emb.set_thumbnail(url="https://i.imgur.com/kJpmRXA.png")
            osumsg = await message.send(embed=emb)
            for emoji in elist:
                await osumsg.add_reaction(emoji)

            def check(reaction, user):
                if reaction.message.id != osumsg.id:
                    return False
                return user == message.author

            try:
                reaction = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
            except asyncio.TimeoutError:
                return False

            if str(reaction[0].emoji) == osust:
                gm = 0
                profile = "Standard"
            elif str(reaction[0].emoji) == osumania:
                gm = 3
                profile = "Mania"
            elif str(reaction[0].emoji) == osutaiko:
                gm = 1
                profile = "Taiko"
            elif str(reaction[0].emoji) == osucatch:
                gm = 2
                profile = "Catch"
        elif mode:
            if mode == "osu" or mode == "OSU" or mode == "osu!" or mode == "OSU!" or mode == "Standard":
                gm = 0
                profile = "Standard"
            elif mode == "mania" or mode == "MANIA" or mode == "Mania":
                gm = 3
                profile = "Mania"
            elif mode == "taiko" or mode == "TAIKO" or mode == "Taiko":
                gm = 1
                profile = "Taiko"
            elif mode == "catch" or mode == "CATCH" or mode == "Catch":
                gm = 2
                profile = "Catch"
            else:
                return await message.send(f"{message.author.mention}, `{mode}`는  없는 게임모드입니다.")
            osumsg = await message.send(f"{message.author.mention}, {name}님의 osu!{profile} 데이터를 검색합니다.")

        rj = self.stats(name, gm)
        await osumsg.clear_reactions()
        if rj == []:
            return await osumsg.edit(content=f"{message.author.mention}, {name}님의 osu!{profile} 데이터를 찾을수 없습니다.", embed=None)
        osuname = rj[0]['username']
        osuuserid = rj[0]['user_id']
        osucountry = rj[0]['country']
        osupp_rank = rj[0]['pp_rank']
        osupp_country_rank = rj[0]['pp_country_rank']
        osulevel = rj[0]['level']
        olevel = osulevel.split(".")
        leval = osulevel[+3:]
        osuaccuracy = rj[0]['accuracy']
        osupp_raw = rj[0]['pp_raw']
        osuplaycount = rj[0]['playcount']
        osucount_rank_ss = rj[0]['count_rank_ss']
        osucount_rank_ssh = rj[0]['count_rank_ssh']
        osucount_rank_s = rj[0]['count_rank_s']
        osucount_rank_sh = rj[0]['count_rank_sh']
        osucount_rank_a = rj[0]['count_rank_a']
        emb = discord.Embed(description=f"""
        **▸ 공식 랭크**: #{osupp_rank} ({osucountry}#{osupp_country_rank})
        **▸ 레벨**: {olevel[0]} ({leval[0:2]}.{leval[2:]}%)
        **▸ 총 PP**: {osupp_raw}
         **▸ 정확도**: {osuaccuracy[:+5]}%
        **▸ 총 플레이**: {osuplaycount}
        {osurssh}: **{osucount_rank_ssh}** | {osurss} : **{osucount_rank_ss}** | {osursh} : **{osucount_rank_sh}** | {osurs} : **{osucount_rank_s}** | {osura} : **{osucount_rank_a}**
        """, color=0xf87fef)
        emb.set_author(
            name=f"osu! {profile} Profile for {osuname}", url=f"https://osu.ppy.sh/users/{osuuserid}/osu", icon_url=data['LenaClient']['flag'][osucountry])
        emb.set_thumbnail(url=f"https://a.ppy.sh/{osuuserid}?.jpeg")
        await osumsg.edit(content=None, embed=emb)


def setup(bot):
    bot.add_cog(osu_command(bot))
