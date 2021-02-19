import discord
import json
import requests
import typing

from riotwatcher import LolWatcher
from discord.ext import commands

with open("./data/bot_config.json", "r", encoding="UTF-8") as f:
    data = json.load(f)
LOL_ICON = data["LenaClient"]["emoji"]["LOL"]
apikey = data['LenaClient']['api']['Riot']['key']
region = "kr"
watcher = LolWatcher(apikey)

rankcolors = {
    "IRONColor": 0x888888,
    "BRONZEColor": 0x947751,
    "SILVERColor": 0xe0e0e0,
    "GOLDColor": 0xecd825,
    "PLATINUMColor": 0x3fcf7f,
    "DIAMONDColor": 0x4a98ee,
    "MASTERColor": 0x7423b3,
    "GRANDMASTERColor": 0x7c2149,
    "CHALLENGERColor": 0xf5eca5
}


class legue_command(commands.Cog, name="Stats"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="롤", alises=["lol", "lolinfo"])
    async def _lolinfo(self, message, *, user: str):
        waitmsg = await message.send(f"{message.author.mention}, 유저를 검색하는중...")
        try:
            summonerinfo = watcher.summoner.by_name(region, user)
        except Exception:
            return await waitmsg.edit(content=f"{message.author.mention}, 존재하지 않는 유저입니다.", embed=None)
        summonername = summonerinfo['name']
        summonericonid = summonerinfo['profileIconId']
        summonerid = summonerinfo['id']
        summonerlv = summonerinfo['summonerLevel']

        summonerranks = watcher.league.by_summoner(region, summonerid)
        my_matches = watcher.match.matchlist_by_account(
            region, summonerinfo['accountId'])

        champ = watcher.champion_mastery.scores_by_summoner(region, summonerid)
        versions = watcher.data_dragon.versions_for_region(region)
        champions_version = versions['n']['champion']

        iconurl = f"http://ddragon.leagueoflegends.com/cdn/{champions_version}/img/profileicon/{summonericonid}.png"
        if summonerranks:
            if len(summonerranks) == 2:
                tierint1 = data['LenaClient']['api']['Riot'][summonerranks[0]['tier']+"i"]
                tierint2 = data['LenaClient']['api']['Riot'][summonerranks[1]['tier']+"i"]
                if tierint1 < tierint2:
                    toprank = summonerranks[1]['tier']
                    rankcolor = rankcolors[summonerranks[1]['tier']+"Color"]
                elif tierint1 > tierint2:
                    toprank = summonerranks[0]['tier']
                    rankcolor = rankcolors[summonerranks[0]['tier']+"Color"]
                elif tierint1 == tierint2:
                    toprank = summonerranks[0]['tier']
                    rankcolor = rankcolors[summonerranks[0]['tier']+"Color"]
            else:
                toprank = summonerranks[0]['tier']
                rankcolor = rankcolors[summonerranks[0]['tier']+"Color"]
        else:
            toprank = "UNRANK"
            rankcolor = 0x2c87c4
        emb = discord.Embed(
            title=f"{LOL_ICON}LOL Profile: {summonername}", description=f"{summonername}님의 리그 오브 레전드 전적입니다.", color=rankcolor)
        emb.set_thumbnail(url=iconurl)
        emb.add_field(name=f"**레벨/지역:**",
                      value=f"{summonerlv} / {region.upper()}")
        emb.add_field(name=f"**숙련도 총점:**",
                      value=f"{champ}")
        lanes = [
            {
                "name": "TOP", "int": 0
            },
            {
                "name": "JUNGLE", "int": 0
            },
            {
                "name": "MID", "int": 0
            },
            {
                "name": "ADC", "int": 0
            },
            {
                "name": "SUPPORT", "int": 0
            }
        ]
        Null = 0
        for pos in my_matches['matches']:
            if pos['lane'] == "MID":
                lanes[2]['int'] += 1
            if pos['lane'] == "TOP":
                lanes[0]['int'] += 1
            if pos['lane'] == "JUNGLE":
                lanes[1]['int'] += 1
            if pos['lane'] == "BOTTOM":
                if pos['role'] == "DUO_SUPPORT":
                    lanes[4]['int'] += 1
                if pos['role'] == "DUO_CARRY":
                    lanes[3]['int'] += 1
            if pos['lane'] == "NONE":
                Null += 1
        lanes = sorted(lanes, key=lambda item: item.get("int"), reverse=True)
        emb.add_field(name=f"**선호 라인:**", value=f"""
        {data['LenaClient']['api']['Riot']['lane'][f'{toprank}_{lanes[0]["name"]}']} **{lanes[0]['name']}:** {("%.0f%%" % (lanes[0]['int'] / (len(my_matches['matches']) - Null) * 100.0))}
        """)
        for rank in summonerranks:
            queuetype = data['LenaClient']['api']['Riot'][rank["queueType"]]
            tier = data['LenaClient']['api']['Riot'][rank['tier']]
            tieremoji = data['LenaClient']['api']['Riot'][rank['tier']+"img"]
            emb.add_field(name=f"**{queuetype}:**", value=f"""
                {tieremoji} **{tier} {rank['rank']}**
                **{rank['leaguePoints']}LP** / {rank['wins']}승 {rank['losses']}패
                승률: {round(rank['wins']/(rank['wins']+rank['losses'])*100, 2)}%
                """, inline=True)
        await waitmsg.edit(content=None, embed=emb)


def setup(bot):
    bot.add_cog(legue_command(bot))
