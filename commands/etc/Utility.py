# pylint: disable=relative-beyond-top-level
# pylint: disable=no-member
# pylint: disable=unused-variable

import json
import discord
import datetime
import os
import requests
import cpuinfo
import psutil
import platform
import datetime
import random
import asyncio
import logging
import typing
import hcskr
import subprocess
import sys

from bs4 import BeautifulSoup
from ..etc import CmdError
from discord.ext.commands import bot
from discord.ext import commands

with open("./data/bot_config.json", "r", encoding="UTF-8") as f:
    data = json.load(f)
Lenaimg = data["LenaClient"]["emoji"]["Lenaimg"]
Client_ICON = data["LenaClient"]["emoji"]["Client"]
Admin_ICON = data["LenaClient"]["emoji"]["Admin"]
Dev_ICON = data["LenaClient"]["emoji"]["Dev"]
Help_ICON = data["LenaClient"]["emoji"]["Help"]
Moder_ICON = data["LenaClient"]["emoji"]["Moder"]
Util_ICON = data["LenaClient"]["emoji"]["Util"]
Economy_ICON = data["LenaClient"]["emoji"]["coin"]
Stats_ICON = data["LenaClient"]["emoji"]["Stats"]
Music_ICON = data["LenaClient"]["emoji"]["Music"]
CPU_ICON = data["LenaClient"]["emoji"]["cpu"]
OS_ICON = data["LenaClient"]["emoji"]["os"]
RAM_ICON = data["LenaClient"]["emoji"]["ram"]
DISCORD_ICON = data["LenaClient"]["emoji"]["discord"]
VERSION_ICON = data["LenaClient"]["emoji"]["version"]
SERVER_ICON = data["LenaClient"]["emoji"]["server"]
USER_ICON = data["LenaClient"]["emoji"]["user"]
CHANNEL_ICON = data["LenaClient"]["emoji"]["channel"]
FUN_ICON = data["LenaClient"]["emoji"]["fun"]
coin = data["LenaClient"]["emoji"]["coin"]
SEASON_ICON = data["LenaClient"]["emoji"]["season"]
Errorimg = data["LenaClient"]["emoji"]["Error"]
Passbookimg = data["LenaClient"]["emoji"]["passbook"]


class LenaCleint_logger:
    handler = logging.FileHandler(
        filename='./data/logs/lenaclient.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter(
        '[%(asctime)s] [%(filename)s] [%(name)s:%(module)s] [%(levelname)s]: %(message)s'))
    discord_logger = logging.getLogger('discord')
    discord_logger.setLevel(logging.WARNING)
    krbot_logger = logging.getLogger('koreanbots')
    krbot_logger.setLevel(logging.DEBUG)
    command_logger = logging.getLogger('commands')
    command_logger.setLevel(logging.INFO)
    moder_logger = logging.getLogger('moderation')
    moder_logger.setLevel(logging.DEBUG)
    # logger
    discord_logger.addHandler(handler)
    krbot_logger.addHandler(handler)
    command_logger.addHandler(handler)
    moder_logger.addHandler(handler)

class Admin:
    def __init__(self, bot):
        self.bot = bot

    class Logger:
        def __init__(self, bot):
            self.bot = bot

        def get_logging_channel(self, guild_id):
            with open('./data/User_Data/logging.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            if str(guild_id) in data:
                logging_channel = self.bot.get_channel(data[str(guild_id)]["channel"])
                if logging_channel is not None:
                    return logging_channel
                else:
                    return None
            else:
                return None

        def get_logging_setting(self, guild_id, sett_name):
            with open('./data/User_Data/logging.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            if str(guild_id) in data:
                return data[str(guild_id)]["settings"][sett_name]
            else:
                return False

class Warnings:
    def __init__(self, bot):
        self.bot = bot

    async def create_data(self, message, user: discord.Member = None):
        with open('./data/Moder_log.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        if str(message.guild.id) not in data:
            data[str(message.guild.id)] = {
                "limit": 5,
                "logging_channel": None,
                "settings": {},
                "temp_bans": {},
                "members": {}
            }
            await message.send(f"{message.author.mention}, **{message.guild.name}**서버의 경고 데이터를 생성하였습니다.\n기본 경고한도는 **`5`**회 입니다.")
        if user:
            if str(user.id) not in data[str(message.guild.id)]["members"]:
                data[str(message.guild.id)]["members"][str(user.id)] = {
                    "warns": 0,
                    "warn_logging": []
                }
        with open('./data/Moder_log.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    async def moder_checked(self, message, user: discord.Member):
        await Warnings.create_data(self, message, user)
        with open('./data/Moder_log.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data[str(message.guild.id)]["members"][str(user.id)]

    async def moder_get_limit(self, message):
        await Warnings.create_data(self, message)
        with open('./data/Moder_log.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data[str(message.guild.id)]

    async def moder_user_ban(self, message, user, delete_message_days, reason):
        await Warnings.create_data(self, message, user)
        with open('./data/Moder_log.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        await user.ban(delete_message_days=delete_message_days, reason=reason)
        del data[str(message.guild.id)]["members"][str(user.id)]
        with open('./data/Moder_log.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    async def moder_warn(self, message, user: discord.Member, Reason: str):
        await Warnings.create_data(self, message, user)
        with open('./data/Moder_log.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        data[str(message.guild.id)]["members"][str(user.id)]["warns"] += 1
        with open('./data/Moder_log.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        LenaCleint_logger.moder_logger.debug(
            f"{message.author} => {user} Warnned")
        await Warnings.moder_addlogging(self, message, user, Reason, True)
        return data[str(message.guild.id)]["members"][str(user.id)]["warns"]

    async def moder_unwarn(self, message, user: discord.Member, Reason: str):
        await Warnings.create_data(self, message, user)
        with open('./data/Moder_log.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        if (data[str(message.guild.id)]["members"]
                [str(user.id)]["warns"] - 1) < 0:
            raise CmdError.Moder.FaileUnwarn
        data[str(message.guild.id)]["members"][str(user.id)]["warns"] += -1
        with open('./data/Moder_log.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        LenaCleint_logger.moder_logger.debug(
            f"{message.author} => {user} UnWarnned")
        await Warnings.moder_addlogging(self, message, user, Reason, False)
        return data[str(message.guild.id)]["members"][str(user.id)]["warns"]

    async def moder_set_limit(self, message, limit: int):
        await Warnings.create_data(self, message)
        with open('./data/Moder_log.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        oldlimit = data[str(message.guild.id)]["limit"]
        data[str(message.guild.id)]["limit"] = limit
        with open('./data/Moder_log.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return oldlimit, limit

    async def moder_set_channel(self, message, channel: discord.TextChannel):
        await Warnings.create_data(self, message)
        with open('./data/Moder_log.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        data[str(message.guild.id)]["logging_channel"] = channel.id
        with open('./data/Moder_log.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return data[str(message.guild.id)]["logging_channel"]

    async def moder_addlogging(self, message, user: discord.Member, Reason: str, Type: bool):
        await Warnings.create_data(self, message, user)
        with open('./data/Moder_log.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        data[str(message.guild.id)]["members"][str(user.id)]["warn_logging"].append({
            "Moder": message.author.id,
            "Type": (True if Type == True else False),
            "Reason": Reason
        })
        if len(data[str(message.guild.id)]["members"]
               [str(user.id)]["warn_logging"]) > 5:
            del data[str(message.guild.id)]["members"][str(
                user.id)]["warn_logging"][0]
        with open('./data/Moder_log.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    async def moder_tempban(self, message, user: discord.Member, days: int, reason: str):
        await Warnings.create_data(self, message)
        with open('./data/Moder_log.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        if str(user.id) not in data[str(message.guild.id)]['temp_bans']:
            now = datetime.datetime.now()
            day = (now + datetime.timedelta(days=days)).strftime("%Y%m%d%H")
            data[str(message.guild.id)]['temp_bans'][str(user.id)] = day
            await Warnings.moder_user_ban(self, message, user, 0, reason)
            with open('./data/Moder_log.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            time = (datetime.datetime.strptime(day, '%Y%m%d%H'))
            return time
        else:
            raise CmdError.Moder.UseTempBan


class Utility:
    def __init__(self, bot):
        self.bot = bot

    def load_cogs(self):
        failed_list = []
        print("레나봇의 명령어를 불러오겠습니다.")
        for folder in data["LenaClient"]["folder"]:
            for cogs in os.listdir(f"commands/{folder}"):
                if cogs.endswith(".py"):
                    try:
                        self.load_extension(f"commands.{folder}.{cogs[:-3]}")
                        print(f"성공 {folder}/{cogs}")
                    except Exception as e:
                        print(f"실패 {e.__class__.__name__}: {e}")
                        failed_list.append(
                            f"{cogs}: {e.__class__.__name__}: {e}\n")
        if failed_list:
            print(f"\n볼러오기를 실패한 파일 \n{''.join(failed_list)}")
        print("완료!")
        return failed_list

    async def reload_cogs(self, message):
        for folder in data["LenaClient"]["folder"]:
            for cogs in os.listdir(f"commands/{folder}"):
                if cogs.endswith(".py"):
                    self.unload_extension(f"commands.{folder}.{cogs[:-3]}")
                    print(f"Unloading {folder}/{cogs}")
        await message.send(f"> {Lenaimg} **Reloading Cogs**")
        await self.logout()
        subprocess.call([sys.executable, "LenaClient.py"])

    def get_duration(self, sec):
        m, s = divmod(sec, 60)
        h, m = divmod(m, 60)
        d, h = divmod(h, 24)

        if d:
            fmt = "{d:02d}:{h:02d}:{m:02d}:{s:02d}"
        elif h:
            fmt = "{h:02d}:{m:02d}:{s:02d}"
        elif m:
            fmt = "{m:02d}:{s:02d}"
        else:
            fmt = "{m:02d}:{s:02d}"
        return fmt.format(d=d, h=h, m=m, s=s)

    def second_convert(self, sec: int):
        m, s = divmod(sec, 60)
        h, m = divmod(m, 60)
        d, h = divmod(h, 24)

        if d:
            fmt = "{d}일 {h}시간 {m}분 {s}초"
        elif h:
            fmt = "{h}시간 {m}분 {s}초"
        elif m:
            fmt = "{m}분 {s}초"
        else:
            fmt = "{s}초"
        return fmt.format(d=d, h=h, m=m, s=s)

    def command_missing_perm(self, message,missing_perms, bot):
        with open("./data/bot_config.json", "r", encoding="UTF-8") as f:
            data = json.load(f)
        perms = []
        for perm in missing_perms:
            perms.append(f"**`{data['LenaClient']['perm'][perm]}`**")
        if bot == False:
            emb = discord.Embed(
                title=f"{Lenaimg} 권한부족 - 유저", color=0x1ab102, timestamp=datetime.datetime.utcnow())
            emb.description = "명령어를 실행하기에는 당신의 권한이 부족합니다.\n필요한 권한을 확인 후 다시 시도하여 주세요."
            emb.add_field(name="**필요한 권한:**", value=str.join(", ", perms))
            emb.set_footer(text=message.author, icon_url=message.author.avatar_url)
        elif bot == True:
            emb = discord.Embed(
                title=f"{Lenaimg} 권한부족 - 봇", color=0x1ab102, timestamp=datetime.datetime.utcnow())
            emb.description = f"명령어를 실행하기에는 {self.bot.user.name}의 권한이 부족합니다.\n필요한 권한을 넣어주신 후에 다시 시도하여 주세요."
            emb.add_field(name="**필요한 권한:**", value=str.join(", ", perms))
            emb.set_footer(text=message.author, icon_url=message.author.avatar_url)
        return emb

    def item_name(self, courier: str, bill: int):
        with open('./data/carriers.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        API_KEY = "WHboIZLPf4qhKqCKgp3WAA"
        if courier in data['item']:
            code = data['item'][courier]
            url = f"https://info.sweettracker.co.kr/api/v1/trackingInfo?t_key={API_KEY}&t_code={code}&t_invoice={bill}"
            header = {"content-type": "application/json;charset=UTF-8"}
            r = requests.get(url, headers=header)
            if r.status_code == 200:
                itemname = (r.json())['itemName']
                if itemname != "":
                    return itemname
                else:
                    return "불러올 수 없습니다."
            else:
                return "불러올 수 없습니다."
        else:
            return "불러올 수 없습니다."

    def nyehuing(self, length):
        nyehui = ["가", "각", "간", "갇", "갈", "갉", "갊", "감", "갑", "값", "갓", "갔", "강", "갖",
                  "갗", "같", "갚", "갛", "개", "객", "갠", "갤", "갬", "갭", "갯", "갰", "갱", "갸",
                  "갹", "갼", "걀", "걋", "걍", "걔", "걘", "걜", "거", "걱", "건", "걷", "걸", "걺",
                  "검", "겁", "것", "겄", "겅", "겆", "겉", "겊", "겋", "게", "겐", "겔", "겜", "겝",
                  "겟", "겠", "겡", "겨", "격", "겪", "견", "겯", "결", "겸", "겹", "겻", "겼", "경",
                  "곁", "계", "곈", "곌", "곕", "곗", "고", "곡", "곤", "곧", "골", "곪", "곬", "곯",
                  "곰", "곱", "곳", "공", "곶", "과", "곽", "관", "괄", "괆", "괌", "괍", "괏", "광",
                  "괘", "괜", "괠", "괩", "괬", "괭", "괴", "괵", "괸", "괼", "굄", "굅", "굇", "굉",
                  "교", "굔", "굘", "굡", "굣", "구", "국", "군", "굳", "굴", "굵", "굶", "굻", "굼",
                  "굽", "굿", "궁", "궂", "궈", "궉", "권", "궐", "궜", "궝", "궤", "궷", "귀", "귁",
                  "귄", "귈", "귐", "귑", "귓", "규", "균", "귤", "그", "극", "근", "귿", "글", "긁",
                  "금", "급", "긋", "긍", "긔", "기", "긱", "긴", "긷", "길", "긺", "김", "깁", "깃",
                  "깅", "깆", "깊", "까", "깍", "깎", "깐", "깔", "깖", "깜", "깝", "깟", "깠", "깡",
                  "깥", "깨", "깩", "깬", "깰", "깸", "깹", "깻", "깼", "깽", "꺄", "꺅", "꺌", "꺼",
                  "꺽", "꺾", "껀", "껄", "껌", "껍", "껏", "껐", "껑", "께", "껙", "껜", "껨", "껫",
                  "껭", "껴", "껸", "껼", "꼇", "꼈", "꼍", "꼐", "꼬", "꼭", "꼰", "꼲", "꼴", "꼼",
                  "꼽", "꼿", "꽁", "꽂", "꽃", "꽈", "꽉", "꽐", "꽜", "꽝", "꽤", "꽥", "꽹", "꾀",
                  "꾄", "꾈", "꾐", "꾑", "꾕", "꾜", "꾸", "꾹", "꾼", "꿀", "꿇", "꿈", "꿉", "꿋",
                  "꿍", "꿎", "꿔", "꿜", "꿨", "꿩", "꿰", "꿱", "꿴", "꿸", "뀀", "뀁", "뀄", "뀌",
                  "뀐", "뀔", "뀜", "뀝", "뀨", "끄", "끅", "끈", "끊", "끌", "끎", "끓", "끔", "끕",
                  "끗", "끙", "끝", "끼", "끽", "낀", "낄", "낌", "낍", "낏", "낑", "나", "낙", "낚",
                  "난", "낟", "날", "낡", "낢", "남", "납", "낫", "났", "낭", "낮", "낯", "낱", "낳",
                  "내", "낵", "낸", "낼", "냄", "냅", "냇", "냈", "냉", "냐", "냑", "냔", "냘", "냠",
                  "냥", "너", "넉", "넋", "넌", "널", "넒", "넓", "넘", "넙", "넛", "넜", "넝", "넣",
                  "네", "넥", "넨", "넬", "넴", "넵", "넷", "넸", "넹", "녀", "녁", "년", "녈", "념",
                  "녑", "녔", "녕", "녘", "녜", "녠", "노", "녹", "논", "놀", "놂", "놈", "놉", "놋",
                  "농", "높", "놓", "놔", "놘", "놜", "놨", "뇌", "뇐", "뇔", "뇜", "뇝", "뇟", "뇨",
                  "뇩", "뇬", "뇰", "뇹", "뇻", "뇽", "누", "눅", "눈", "눋", "눌", "눔", "눕", "눗",
                  "눙", "눠", "눴", "눼", "뉘", "뉜", "뉠", "뉨", "뉩", "뉴", "뉵", "뉼", "늄", "늅",
                  "늉", "느", "늑", "는", "늘", "늙", "늚", "늠", "늡", "늣", "능", "늦", "늪", "늬",
                  "늰", "늴", "니", "닉", "닌", "닐", "닒", "님", "닙", "닛", "닝", "닢", "다", "닥",
                  "닦", "단", "닫", "달", "닭", "닮", "닯", "닳", "담", "답", "닷", "닸", "당", "닺",
                  "닻", "닿", "대", "댁", "댄", "댈", "댐", "댑", "댓", "댔", "댕", "댜", "더", "덕",
                  "덖", "던", "덛", "덜", "덞", "덟", "덤", "덥", "덧", "덩", "덫", "덮", "데", "덱",
                  "덴", "델", "뎀", "뎁", "뎃", "뎄", "뎅", "뎌", "뎐", "뎔", "뎠", "뎡", "뎨", "뎬",
                  "도", "독", "돈", "돋", "돌", "돎", "돐", "돔", "돕", "돗", "동", "돛", "돝", "돠",
                  "돤", "돨", "돼", "됐", "되", "된", "될", "됨", "됩", "됫", "됴", "두", "둑", "둔",
                  "둘", "둠", "둡", "둣", "둥", "둬", "뒀", "뒈", "뒝", "뒤", "뒨", "뒬", "뒵", "뒷",
                  "뒹", "듀", "듄", "듈", "듐", "듕", "드", "득", "든", "듣", "들", "듦", "듬", "듭",
                  "듯", "등", "듸", "디", "딕", "딘", "딛", "딜", "딤", "딥", "딧", "딨", "딩", "딪",
                  "따", "딱", "딴", "딸", "땀", "땁", "땃", "땄", "땅", "땋", "때", "땍", "땐", "땔",
                  "땜", "땝", "땟", "땠", "땡", "떠", "떡", "떤", "떨", "떪", "떫", "떰", "떱", "떳",
                  "떴", "떵", "떻", "떼", "떽", "뗀", "뗄", "뗌", "뗍", "뗏", "뗐", "뗑", "뗘", "뗬",
                  "또", "똑", "똔", "똘", "똥", "똬", "똴", "뙈", "뙤", "뙨", "뚜", "뚝", "뚠", "뚤",
                  "뚫", "뚬", "뚱", "뛔", "뛰", "뛴", "뛸", "뜀", "뜁", "뜅", "뜨", "뜩", "뜬", "뜯",
                  "뜰", "뜸", "뜹", "뜻", "띄", "띈", "띌", "띔", "띕", "띠", "띤", "띨", "띰", "띱",
                  "띳", "띵", "라", "락", "란", "랄", "람", "랍", "랏", "랐", "랑", "랒", "랖", "랗",
                  "래", "랙", "랜", "랠", "램", "랩", "랫", "랬", "랭", "랴", "략", "랸", "럇", "량",
                  "러", "럭", "런", "럴", "럼", "럽", "럿", "렀", "렁", "렇", "레", "렉", "렌", "렐",
                  "렘", "렙", "렛", "렝", "려", "력", "련", "렬", "렴", "렵", "렷", "렸", "령", "례",
                  "롄", "롑", "롓", "로", "록", "론", "롤", "롬", "롭", "롯", "롱", "롸", "롼", "뢍",
                  "뢨", "뢰", "뢴", "뢸", "룀", "룁", "룃", "룅", "료", "룐", "룔", "룝", "룟", "룡",
                  "루", "룩", "룬", "룰", "룸", "룹", "룻", "룽", "뤄", "뤘", "뤠", "뤼", "뤽", "륀",
                  "륄", "륌", "륏", "륑", "류", "륙", "륜", "률", "륨", "륩", "륫", "륭", "르", "륵",
                  "른", "를", "름", "릅", "릇", "릉", "릊", "릍", "릎", "리", "릭", "린", "릴", "림",
                  "립", "릿", "링", "마", "막", "만", "많", "맏", "말", "맑", "맒", "맘", "맙", "맛",
                  "망", "맞", "맡", "맣", "매", "맥", "맨", "맬", "맴", "맵", "맷", "맸", "맹", "맺",
                  "먀", "먁", "먈", "먕", "머", "먹", "먼", "멀", "멂", "멈", "멉", "멋", "멍", "멎",
                  "멓", "메", "멕", "멘", "멜", "멤", "멥", "멧", "멨", "멩", "며", "멱", "면", "멸",
                  "몃", "몄", "명", "몇", "몌", "모", "목", "몫", "몬", "몰", "몲", "몸", "몹", "못",
                  "몽", "뫄", "뫈", "뫘", "뫙", "뫼", "묀", "묄", "묍", "묏", "묑", "묘", "묜", "묠",
                  "묩", "묫", "무", "묵", "묶", "문", "묻", "물", "묽", "묾", "뭄", "뭅", "뭇", "뭉",
                  "뭍", "뭏", "뭐", "뭔", "뭘", "뭡", "뭣", "뭬", "뮈", "뮌", "뮐", "뮤", "뮨", "뮬",
                  "뮴", "뮷", "므", "믄", "믈", "믐", "믓", "미", "믹", "민", "믿", "밀", "밂", "밈",
                  "밉", "밋", "밌", "밍", "및", "밑", "바", "박", "밖", "밗", "반", "받", "발", "밝",
                  "밞", "밟", "밤", "밥", "밧", "방", "밭", "배", "백", "밴", "밸", "뱀", "뱁", "뱃",
                  "뱄", "뱅", "뱉", "뱌", "뱍", "뱐", "뱝", "버", "벅", "번", "벋", "벌", "벎", "범",
                  "법", "벗", "벙", "벚", "베", "벡", "벤", "벧", "벨", "벰", "벱", "벳", "벴", "벵",
                  "벼", "벽", "변", "별", "볍", "볏", "볐", "병", "볕", "볘", "볜", "보", "복", "볶",
                  "본", "볼", "봄", "봅", "봇", "봉", "봐", "봔", "봤", "봬", "뵀", "뵈", "뵉", "뵌",
                  "뵐", "뵘", "뵙", "뵤", "뵨", "부", "북", "분", "붇", "불", "붉", "붊", "붐", "붑",
                  "붓", "붕", "붙", "붚", "붜", "붤", "붰", "붸", "뷔", "뷕", "뷘", "뷜", "뷩", "뷰",
                  "뷴", "뷸", "븀", "븃", "븅", "브", "븍", "븐", "블", "븜", "븝", "븟", "비", "빅",
                  "빈", "빌", "빎", "빔", "빕", "빗", "빙", "빚", "빛", "빠", "빡", "빤", "빨", "빪",
                  "빰", "빱", "빳", "빴", "빵", "빻", "빼", "빽", "뺀", "뺄", "뺌", "뺍", "뺏", "뺐",
                  "뺑", "뺘", "뺙", "뺨", "뻐", "뻑", "뻔", "뻗", "뻘", "뻠", "뻣", "뻤", "뻥", "뻬",
                  "뼁", "뼈", "뼉", "뼘", "뼙", "뼛", "뼜", "뼝", "뽀", "뽁", "뽄", "뽈", "뽐", "뽑",
                  "뽕", "뾔", "뾰", "뿅", "뿌", "뿍", "뿐", "뿔", "뿜", "뿟", "뿡", "쀼", "쁑", "쁘",
                  "쁜", "쁠", "쁨", "쁩", "삐", "삑", "삔", "삘", "삠", "삡", "삣", "삥", "사", "삭",
                  "삯", "산", "삳", "살", "삵", "삶", "삼", "삽", "삿", "샀", "상", "샅", "새", "색",
                  "샌", "샐", "샘", "샙", "샛", "샜", "생", "샤", "샥", "샨", "샬", "샴", "샵", "샷",
                  "샹", "섀", "섄", "섈", "섐", "섕", "서", "석", "섞", "섟", "선", "섣", "설", "섦",
                  "섧", "섬", "섭", "섯", "섰", "성", "섶", "세", "섹", "센", "셀", "셈", "셉", "셋",
                  "셌", "셍", "셔", "셕", "션", "셜", "셤", "셥", "셧", "셨", "셩", "셰", "셴", "셸",
                  "솅", "소", "속", "솎", "손", "솔", "솖", "솜", "솝", "솟", "송", "솥", "솨", "솩",
                  "솬", "솰", "솽", "쇄", "쇈", "쇌", "쇔", "쇗", "쇘", "쇠", "쇤", "쇨", "쇰", "쇱",
                  "쇳", "쇼", "쇽", "숀", "숄", "숌", "숍", "숏", "숑", "수", "숙", "순", "숟", "술",
                  "숨", "숩", "숫", "숭", "숯", "숱", "숲", "숴", "쉈", "쉐", "쉑", "쉔", "쉘", "쉠",
                  "쉥", "쉬", "쉭", "쉰", "쉴", "쉼", "쉽", "쉿", "슁", "슈", "슉", "슐", "슘", "슛",
                  "슝", "스", "슥", "슨", "슬", "슭", "슴", "습", "슷", "승", "시", "식", "신", "싣",
                  "실", "싫", "심", "십", "싯", "싱", "싶", "싸", "싹", "싻", "싼", "쌀", "쌈", "쌉",
                  "쌌", "쌍", "쌓", "쌔", "쌕", "쌘", "쌜", "쌤", "쌥", "쌨", "쌩", "썅", "써", "썩",
                  "썬", "썰", "썲", "썸", "썹", "썼", "썽", "쎄", "쎈", "쎌", "쏀", "쏘", "쏙", "쏜",
                  "쏟", "쏠", "쏢", "쏨", "쏩", "쏭", "쏴", "쏵", "쏸", "쐈", "쐐", "쐤", "쐬", "쐰",
                  "쐴", "쐼", "쐽", "쑈", "쑤", "쑥", "쑨", "쑬", "쑴", "쑵", "쑹", "쒀", "쒔", "쒜",
                  "쒸", "쒼", "쓩", "쓰", "쓱", "쓴", "쓸", "쓺", "쓿", "씀", "씁", "씌", "씐", "씔",
                  "씜", "씨", "씩", "씬", "씰", "씸", "씹", "씻", "씽", "아", "악", "안", "앉", "않",
                  "알", "앍", "앎", "앓", "암", "압", "앗", "았", "앙", "앝", "앞", "애", "액", "앤",
                  "앨", "앰", "앱", "앳", "앴", "앵", "야", "약", "얀", "얄", "얇", "얌", "얍", "얏",
                  "양", "얕", "얗", "얘", "얜", "얠", "얩", "어", "억", "언", "얹", "얻", "얼", "얽",
                  "얾", "엄", "업", "없", "엇", "었", "엉", "엊", "엌", "엎", "에", "엑", "엔", "엘",
                  "엠", "엡", "엣", "엥", "여", "역", "엮", "연", "열", "엶", "엷", "염", "엽", "엾",
                  "엿", "였", "영", "옅", "옆", "옇", "예", "옌", "옐", "옘", "옙", "옛", "옜", "오",
                  "옥", "온", "올", "옭", "옮", "옰", "옳", "옴", "옵", "옷", "옹", "옻", "와", "왁",
                  "완", "왈", "왐", "왑", "왓", "왔", "왕", "왜", "왝", "왠", "왬", "왯", "왱", "외",
                  "왹", "왼", "욀", "욈", "욉", "욋", "욍", "요", "욕", "욘", "욜", "욤", "욥", "욧",
                  "용", "우", "욱", "운", "울", "욹", "욺", "움", "웁", "웃", "웅", "워", "웍", "원",
                  "월", "웜", "웝", "웠", "웡", "웨", "웩", "웬", "웰", "웸", "웹", "웽", "위", "윅",
                  "윈", "윌", "윔", "윕", "윗", "윙", "유", "육", "윤", "율", "윰", "윱", "윳", "융",
                  "윷", "으", "윽", "은", "을", "읊", "음", "읍", "읏", "응", "읒", "읓", "읔", "읕",
                  "읖", "읗", "의", "읜", "읠", "읨", "읫", "이", "익", "인", "일", "읽", "읾", "잃",
                  "임", "입", "잇", "있", "잉", "잊", "잎", "자", "작", "잔", "잖", "잗", "잘", "잚",
                  "잠", "잡", "잣", "잤", "장", "잦", "재", "잭", "잰", "잴", "잼", "잽", "잿", "쟀",
                  "쟁", "쟈", "쟉", "쟌", "쟎", "쟐", "쟘", "쟝", "쟤", "쟨", "쟬", "저", "적", "전",
                  "절", "젊", "점", "접", "젓", "정", "젖", "제", "젝", "젠", "젤", "젬", "젭", "젯",
                  "젱", "져", "젼", "졀", "졈", "졉", "졌", "졍", "졔", "조", "족", "존", "졸", "졺",
                  "좀", "좁", "좃", "종", "좆", "좇", "좋", "좌", "좍", "좔", "좝", "좟", "좡", "좨",
                  "좼", "좽", "죄", "죈", "죌", "죔", "죕", "죗", "죙", "죠", "죡", "죤", "죵", "주",
                  "죽", "준", "줄", "줅", "줆", "줌", "줍", "줏", "중", "줘", "줬", "줴", "쥐", "쥑",
                  "쥔", "쥘", "쥠", "쥡", "쥣", "쥬", "쥰", "쥴", "쥼", "즈", "즉", "즌", "즐", "즘",
                  "즙", "즛", "증", "지", "직", "진", "짇", "질", "짊", "짐", "집", "짓", "징", "짖",
                  "짙", "짚", "짜", "짝", "짠", "짢", "짤", "짧", "짬", "짭", "짯", "짰", "짱", "째",
                  "짹", "짼", "쨀", "쨈", "쨉", "쨋", "쨌", "쨍", "쨔", "쨘", "쨩", "쩌", "쩍", "쩐",
                  "쩔", "쩜", "쩝", "쩟", "쩠", "쩡", "쩨", "쩽", "쪄", "쪘", "쪼", "쪽", "쫀", "쫄",
                  "쫌", "쫍", "쫏", "쫑", "쫓", "쫘", "쫙", "쫠", "쫬", "쫴", "쬈", "쬐", "쬔", "쬘",
                  "쬠", "쬡", "쭁", "쭈", "쭉", "쭌", "쭐", "쭘", "쭙", "쭝", "쭤", "쭸", "쭹", "쮜",
                  "쮸", "쯔", "쯤", "쯧", "쯩", "찌", "찍", "찐", "찔", "찜", "찝", "찡", "찢", "찧",
                  "차", "착", "찬", "찮", "찰", "참", "찹", "찻", "찼", "창", "찾", "채", "책", "챈",
                  "챌", "챔", "챕", "챗", "챘", "챙", "챠", "챤", "챦", "챨", "챰", "챵", "처", "척",
                  "천", "철", "첨", "첩", "첫", "첬", "청", "체", "첵", "첸", "첼", "쳄", "쳅", "쳇",
                  "쳉", "쳐", "쳔", "쳤", "쳬", "쳰", "촁", "초", "촉", "촌", "촐", "촘", "촙", "촛",
                  "총", "촤", "촨", "촬", "촹", "최", "쵠", "쵤", "쵬", "쵭", "쵯", "쵱", "쵸", "춈",
                  "추", "축", "춘", "출", "춤", "춥", "춧", "충", "춰", "췄", "췌", "췐", "취", "췬",
                  "췰", "췸", "췹", "췻", "췽", "츄", "츈", "츌", "츔", "츙", "츠", "측", "츤", "츨",
                  "츰", "츱", "츳", "층", "치", "칙", "친", "칟", "칠", "칡", "침", "칩", "칫", "칭",
                  "카", "칵", "칸", "칼", "캄", "캅", "캇", "캉", "캐", "캑", "캔", "캘", "캠", "캡",
                  "캣", "캤", "캥", "캬", "캭", "컁", "커", "컥", "컨", "컫", "컬", "컴", "컵", "컷",
                  "컸", "컹", "케", "켁", "켄", "켈", "켐", "켑", "켓", "켕", "켜", "켠", "켤", "켬",
                  "켭", "켯", "켰", "켱", "켸", "코", "콕", "콘", "콜", "콤", "콥", "콧", "콩", "콰",
                  "콱", "콴", "콸", "쾀", "쾅", "쾌", "쾡", "쾨", "쾰", "쿄", "쿠", "쿡", "쿤", "쿨",
                  "쿰", "쿱", "쿳", "쿵", "쿼", "퀀", "퀄", "퀑", "퀘", "퀭", "퀴", "퀵", "퀸", "퀼",
                  "큄", "큅", "큇", "큉", "큐", "큔", "큘", "큠", "크", "큭", "큰", "클", "큼", "큽",
                  "킁", "키", "킥", "킨", "킬", "킴", "킵", "킷", "킹", "타", "탁", "탄", "탈", "탉",
                  "탐", "탑", "탓", "탔", "탕", "태", "택", "탠", "탤", "탬", "탭", "탯", "탰", "탱",
                  "탸", "턍", "터", "턱", "턴", "털", "턺", "텀", "텁", "텃", "텄", "텅", "테", "텍",
                  "텐", "텔", "템", "텝", "텟", "텡", "텨", "텬", "텼", "톄", "톈", "토", "톡", "톤",
                  "톨", "톰", "톱", "톳", "통", "톺", "톼", "퇀", "퇘", "퇴", "퇸", "툇", "툉", "툐",
                  "투", "툭", "툰", "툴", "툼", "툽", "툿", "퉁", "퉈", "퉜", "퉤", "튀", "튁", "튄",
                  "튈", "튐", "튑", "튕", "튜", "튠", "튤", "튬", "튱", "트", "특", "튼", "튿", "틀",
                  "틂", "틈", "틉", "틋", "틔", "틘", "틜", "틤", "틥", "티", "틱", "틴", "틸", "팀",
                  "팁", "팃", "팅", "파", "팍", "팎", "판", "팔", "팖", "팜", "팝", "팟", "팠", "팡",
                  "팥", "패", "팩", "팬", "팰", "팸", "팹", "팻", "팼", "팽", "퍄", "퍅", "퍼", "퍽",
                  "펀", "펄", "펌", "펍", "펏", "펐", "펑", "페", "펙", "펜", "펠", "펨", "펩", "펫",
                  "펭", "펴", "편", "펼", "폄", "폅", "폈", "평", "폐", "폘", "폡", "폣", "포", "폭",
                  "폰", "폴", "폼", "폽", "폿", "퐁", "퐈", "퐝", "푀", "푄", "표", "푠", "푤", "푭",
                  "푯", "푸", "푹", "푼", "푿", "풀", "풂", "품", "풉", "풋", "풍", "풔", "풩", "퓌",
                  "퓐", "퓔", "퓜", "퓟", "퓨", "퓬", "퓰", "퓸", "퓻", "퓽", "프", "픈", "플", "픔",
                  "픕", "픗", "피", "픽", "핀", "필", "핌", "핍", "핏", "핑", "하", "학", "한", "할",
                  "핥", "함", "합", "핫", "항", "해", "핵", "핸", "핼", "햄", "햅", "햇", "했", "행",
                  "햐", "향", "허", "헉", "헌", "헐", "헒", "험", "헙", "헛", "헝", "헤", "헥", "헨",
                  "헬", "헴", "헵", "헷", "헹", "혀", "혁", "현", "혈", "혐", "협", "혓", "혔", "형",
                  "혜", "혠", "혤", "혭", "호", "혹", "혼", "홀", "홅", "홈", "홉", "홋", "홍", "홑",
                  "화", "확", "환", "활", "홧", "황", "홰", "홱", "홴", "횃", "횅", "회", "획", "횐",
                  "횔", "횝", "횟", "횡", "효", "횬", "횰", "횹", "횻", "후", "훅", "훈", "훌", "훑",
                  "훔", "훗", "훙", "훠", "훤", "훨", "훰", "훵", "훼", "훽", "휀", "휄", "휑", "휘",
                  "휙", "휜", "휠", "휨", "휩", "휫", "휭", "휴", "휵", "휸", "휼", "흄", "흇", "흉",
                  "흐", "흑", "흔", "흖", "흗", "흘", "흙", "흠", "흡", "흣", "흥", "흩", "희", "흰",
                  "흴", "흼", "흽", "힁", "히", "힉", "힌", "힐", "힘", "힙", "힛", "힝"]
        name = ""
        for i in range(length):
            name += nyehui[random.randint(0, len(nyehui) - 1)]
        return name

    class Client:
        def __init__(self, bot):
            self.bot = bot
        
        async def command_help_embeds(self, message, command):
            with open("./data/help_commands.json", "r", encoding="UTF-8") as f:
                helpc = json.load(f)
            embeds = []
            helping = self.bot.get_command(command)
            if helping is None:
                raise CmdError.Client.Not_Commands
            if helping.parent is not None:
                helping = helping.parent
            if str(helping.cog_name) not in helpc or str(
                    helping.name) not in helpc[str(helping.cog_name)]:
                raise CmdError.Client.Commands_NotHelping(str(helping.name))
            helpc = helpc[str(helping.cog_name)]
            emb = discord.Embed(
                title=f"{Help_ICON} {helping.cog_name} - {helping.name}",
                description=helpc[str(helping.name)]["dec"],
                color=self.bot.__color__,
                timestamp=datetime.datetime.utcnow())
            for filed in helpc[str(helping.name)]["fileds"]:
                emb.add_field(
                    name=filed["name"],
                    value=filed["value"].replace(
                        "{prefix}", "e!").replace(
                        "{cmd}", helping.name),
                    inline=filed["inline"])
            embeds.append(emb)
            aliases_emb = ""
            if helping.aliases:
                aliases = []
                for cmd_aliases in helping.aliases:
                    aliases.append(f"**`{cmd_aliases}`**")
                aliases_emb += f"**{helping.name}:** " + \
                    str.join(", ", aliases) + "\n"
                if helpc[str(helping.name)]["group"] == True:
                    for sub_cmd in list(helping.commands):
                        if sub_cmd.aliases:
                            aliases = []
                            for cmd_aliases in sub_cmd.aliases:
                                aliases.append(f"**`{cmd_aliases}`**")
                            aliases_emb += f"**{sub_cmd.name}:** " + \
                                str.join(", ", aliases) + "\n"
                    if "sub_commands" in helpc[str(helping.name)]:
                        sub_commands = helpc[str(helping.name)]["sub_commands"]
                        for sub_command in list(helping.commands):
                            sub_emb = discord.Embed(
                                color=self.bot.__color__,
                                timestamp=datetime.datetime.utcnow())
                            sub_emb.title = f"{Help_ICON} {helping.cog_name} - {sub_command.parent.name} {sub_command.name}"
                            sub_emb.description = sub_commands[str(
                                sub_command.name)]["dec"]
                            for filed in sub_commands[str(
                                    sub_command.name)]["fileds"]:
                                sub_emb.add_field(
                                    name=filed["name"],
                                    value=filed["value"].replace(
                                        "{prefix}", "e!").replace(
                                        "{cmd}", helping.name).replace("{sub_cmd}", sub_command.name),
                                    inline=filed["inline"])
                            embeds.append(sub_emb)
            for emb in embeds:
                if aliases_emb:
                    emb.add_field(name="> ✨ __**단축어:**__", value=aliases_emb)
                emb.set_footer(
                    text=message.author,
                    icon_url=message.author.avatar_url)
            return embeds

        async def command_help(self, message, command, content:str = None):
            embeds = await Utility.Client.command_help_embeds(self, message, command)
            paginator = Paginator(self.bot, message, embeds, normal_emoji=True, embed_content=content, autofooter=True)
            await paginator.run()

    class Diagnosis:
        def __init__(self, bot):
            self.bot = bot

        async def auto_diagnosis(self):
            with open('./data/User_Data/diagnosis.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            if int(datetime.datetime.now().strftime("%H%M")) >= (820 + random.randint(0, 5)) and int(datetime.datetime.now().strftime("%Y%m%d")) > int(data["lastday"]):
                data["lastday"] = datetime.datetime.now().strftime("%Y%m%d")
                udata = data["Users"]
                for user in list(udata.keys()):
                    if udata[str(user)]["skip"] == False:
                        await Utility.Diagnosis.diagnosis(self, str(user))
                    elif udata[str(user)]["skip"] == True:
                        data["Users"][str(user)]["skip"] = False
                        await self.bot.get_user(int(user)).send(f"{self.bot.get_user(int(user)).mention}, 오늘 자동 자가진단 건너뛰기 되어서\n자동 자가진단 건너뛰기가 **비활성화** 되었습니다.")
                with open('./data/User_Data/diagnosis.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)

        async def diagnosis(self, id):
            with open('./data/User_Data/diagnosis.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            if str(id) not in data["Users"]:
                raise CmdError.Season.UserNotInData 
            udata = data["Users"][str(id)]
            edata = await hcskr.asyncSelfCheck(udata["name"], udata["birthday"], udata["city"], udata["school"], udata["school_type"], udata["password"])
            await self.bot.get_user(int(id)).send(f"{self.bot.get_user(int(id)).mention}, {edata['message']}\n**시간:** {(datetime.datetime.now()).strftime('%Y년 %m월 %d일 %p %I시 %M분').replace('PM', '오후').replace('AM', '오전')}")

        async def register(self, message, user: discord.Member, name: str, birthday: str, city: str, school: str, school_Type: str, password: str):
            with open('./data/User_Data/diagnosis.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            if str(user.id) in data["Users"]:
                raise CmdError.Season.UserInData
            data["Users"][str(user.id)] = {
                "skip": False,
                "name": name,
                "birthday": birthday,
                "city": city,
                "school": school,
                "school_type": school_Type,
                "password": password
            }
            with open('./data/User_Data/diagnosis.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            await Utility.Diagnosis.diagnosis(self, user.id)

        async def account_withdrawal(self, message):
            with open('./data/User_Data/diagnosis.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            if str(message.author.id) not in data["Users"]:
                raise CmdError.Season.UserNotInData
            del data["Users"][str(message.author.id)]
            with open('./data/User_Data/diagnosis.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)

        async def skip_settings(self, user: discord.Member):
            with open('./data/User_Data/diagnosis.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            if str(user.id) not in data["Users"]:
                raise CmdError.Season.UserNotInData
            if data["Users"][str(user.id)]["skip"] == True:
                data["Users"][str(user.id)]["skip"] = False
            elif data["Users"][str(user.id)]["skip"] == False:
                data["Users"][str(user.id)]["skip"] = True
            with open('./data/User_Data/diagnosis.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            return data["Users"][str(user.id)]["skip"]

        async def register_event(self, message, user):
            emb = discord.Embed(
                    color=0xc20000,
                    timestamp=datetime.datetime.utcnow())
            emb.description = f"{Errorimg}**주의사항**\n이 명령어는 자신의 개인정보를 수집합니다.\n개인정보는 오직 자동자가진단 목적으로 사용되며\n개발진들은 소중한 유저들의 개인정보를 유출하지 않습니다.\n또한 레나봇이 과부하로 인해 자동자가진단이 실행되지 않아 발생되는 문제는 책임지지 않습니다.\n\n위 사항을 동의하신다면 **`동의`** 아니라면 **`비동의`**를 입력하여주세요."
            msg = await message.send(embed=emb)

            def msg_check(msg):
                return msg.author == message.author and msg.channel == message.channel

            warning = False
            name = None
            birthday = None
            city = None
            school = None
            school_type = None
            password = None

            while not warning == True:
                try:
                    tmsg = await self.bot.wait_for("message", timeout=60, check=msg_check)
                except asyncio.TimeoutError:
                    raise CmdError.Client.message_timeout

                if str(tmsg.content) == "동의":
                    warning = True

                elif str(tmsg.content) == "비동의":
                    return

            await message.send(f"{message.author.mention}, **{datetime.datetime.now().strftime('%Y년 %m월 %d일')}** 개인정보 약관을 동의하였습니다.")
            
            waitname = "홍길동"
            await msg.edit(content=f"자신의 **본명**을 입력하여주세요.\n\n이름: {waitname}\n\n이 작업을 완료하였다면 **`완료`** 작업을 취소하시려면 **`취소`**를 입력하여 주세요.", embed=None)
            while name == None:
                try:
                    tmsg = await self.bot.wait_for("message", timeout=60, check=msg_check)
                except asyncio.TimeoutError:
                    raise CmdError.Client.message_timeout

                if str(tmsg.content) == "완료":
                    name = waitname
                    break
                elif str(tmsg.content) == "취소":
                    return await msg.edit(content=f"**취소**되었습니다.", embed=None)

                waitname = str(tmsg.content)
                await msg.edit(content=f"자신의 **본명**을 입력하여주세요.\n\n이름: {waitname}\n\n이 작업을 완료하였다면 **`완료`** 작업을 취소하시려면 **`취소`**를 입력하여 주세요.")

            waitbirthday = "YYMMDD"
            await msg.edit(content=f"자신의 **생년월일 6자리**를 입력하여주세요.\n\n생년월일: {waitbirthday} : **`YYMMDD`**\n\n이 작업을 완료하였다면 **`완료`** 작업을 취소하시려면 **`취소`**를 입력하여 주세요.")
            while birthday == None:
                try:
                    tmsg = await self.bot.wait_for("message", timeout=60, check=msg_check)
                except asyncio.TimeoutError:
                    raise CmdError.Client.message_timeout

                if str(tmsg.content) == "완료":
                    birthday = waitbirthday
                    break
                elif str(tmsg.content) == "취소":
                    return await msg.edit(content=f"**취소**되었습니다.", embed=None)

                if len(str(tmsg.content)) == 6:
                    waitbirthday = str(tmsg.content)
                await msg.edit(content=f"자신의 **생년월일 6자리**를 입력하여주세요.\n\n생년월일: {waitbirthday} : **`YYMMDD`**\n\n이 작업을 완료하였다면 **`완료`** 작업을 취소하시려면 **`취소`**를 입력하여 주세요.")

            waitcity = "서울"
            await msg.edit(content=f"자신의 **거주지역**을 입력하여주세요.\n\n거주지역: {waitcity}\n\n이 작업을 완료하였다면 **`완료`** 작업을 취소하시려면 **`취소`**를 입력하여 주세요.")
            while city == None:
                try:
                    tmsg = await self.bot.wait_for("message", timeout=60, check=msg_check)
                except asyncio.TimeoutError:
                    raise CmdError.Client.message_timeout

                if str(tmsg.content) == "완료":
                    city = waitcity
                    break
                elif str(tmsg.content) == "취소":
                    return await msg.edit(content=f"**취소**되었습니다.", embed=None)

                waitcity = str(tmsg.content)
                await msg.edit(content=f"자신의 **거주지역**을 입력하여주세요.\n\n거주지역: {waitcity}\n\n이 작업을 완료하였다면 **`완료`** 작업을 취소하시려면 **`취소`**를 입력하여 주세요.")

            waitschool = "레나중"
            await msg.edit(content=f"자신이 다니고있는 **학교명**을 입력하여주세요.\n\n학교명: {waitschool}\n\n이 작업을 완료하였다면 **`완료`** 작업을 취소하시려면 **`취소`**를 입력하여 주세요.")
            while school == None:
                try:
                    tmsg = await self.bot.wait_for("message", timeout=60, check=msg_check)
                except asyncio.TimeoutError:
                    raise CmdError.Client.message_timeout

                if str(tmsg.content) == "완료":
                    school = waitschool
                    break
                elif str(tmsg.content) == "취소":
                    return await msg.edit(content=f"**취소**되었습니다.", embed=None)

                waitschool = str(tmsg.content)
                await msg.edit(content=f"자신이 다니고있는 **학교명**을 입력하여주세요.\n\n학교명: {waitschool}\n\n이 작업을 완료하였다면 **`완료`** 작업을 취소하시려면 **`취소`**를 입력하여 주세요.")
                
            waitschool_type = "중학교"
            await msg.edit(content=f"자신이 다니고있는 **학교급**을 입력하여주세요.\n\n학교급: {waitschool_type}\n\n이 작업을 완료하였다면 **`완료`** 작업을 취소하시려면 **`취소`**를 입력하여 주세요.")
            while school_type == None:
                try:
                    tmsg = await self.bot.wait_for("message", timeout=60, check=msg_check)
                except asyncio.TimeoutError:
                    raise CmdError.Client.message_timeout

                if str(tmsg.content) == "완료":
                    school_type = waitschool_type
                    break
                elif str(tmsg.content) == "취소":
                    return await msg.edit(content=f"**취소**되었습니다.", embed=None)

                school_types = ["유치원", "초등학교", "중학교", "고등학교", "특수학교"]
                if str(tmsg.content) in school_types:
                    waitschool_type = str(tmsg.content)
                    await msg.edit(content=f"자신이 다니고있는 **학교급**을 입력하여주세요.\n\n학교급: {waitschool_type}\n\n이 작업을 완료하였다면 **`완료`** 작업을 취소하시려면 **`취소`**를 입력하여 주세요.")
                else:
                    await message.send("\"" + str.join(", ", school_types) + "\" 중에서 입력하여주세요.")

            waitpassword = "0000"
            await msg.edit(content=f"자신이 자가진단에 사용하고있는 **패스워드**를 입력하여주세요.\n\n패스워드: {waitpassword}\n\n이 작업을 완료하였다면 **`완료`** 작업을 취소하시려면 **`취소`**를 입력하여 주세요.")
            while password == None:
                try:
                    tmsg = await self.bot.wait_for("message", timeout=60, check=msg_check)
                except asyncio.TimeoutError:
                    raise CmdError.Client.message_timeout

                if str(tmsg.content) == "완료":
                    password = waitpassword
                    break
                elif str(tmsg.content) == "취소":
                    return await msg.edit(content=f"**취소**되었습니다.", embed=None)

                waitpassword = str(tmsg.content)
                await msg.edit(content=f"자신이 자가진단에 사용하고있는 **패스워드**를 입력하여주세요.\n\n패스워드: {waitpassword}\n\n이 작업을 완료하였다면 **`완료`** 작업을 취소하시려면 **`취소`**를 입력하여 주세요.")

            await msg.edit(content=f"{message.author.mention}, 정삭적으로 등록됬는지 확인하기 위하여 자가진단을 한번 자동으로 실행합니다.")
            await Utility.Diagnosis.register(self, message, user, name, birthday, city, school, school_type, password)

class Paginator:
    def __init__(
        self,
        client: typing.Union[
            discord.Client,
            discord.AutoShardedClient,
            commands.Bot,
            commands.AutoShardedBot,
        ],
        message: discord.Message,
        embeds: typing.Optional[typing.List[discord.Embed]],
        timeout: int = 30,
        autofooter: bool = False,
        remove_reaction: bool = True,
        embed_content: str = None,
        normal_emoji=False,
        current_page: int = 0
    ) -> None:
        self.message = message
        self.control_emojis = []
        self.control_commands = []
        self.bot = client
        self.embeds = embeds
        self.timeout = timeout
        self.autofooter = autofooter
        self.remove_reaction = remove_reaction
        self.embed_content = embed_content
        self.normal_emoji = normal_emoji

        self.current_page = current_page

    def add_emoji(self, emoji, command):
        self.control_emojis.append(emoji)
        self.control_commands.append(command)

    async def run(self):
        if not (len(self.embeds) - 1) >= self.current_page:
            raise CmdError.Client.Not_Page(str(len(self.embeds)))
        if len(self.embeds) == 1:
            return await self.message.send(embed=self.embeds[0], content=self.embed_content)
        if self.normal_emoji == True:
            self.add_emoji('⏮️', "first")
            self.add_emoji('⏪', "back")
            self.add_emoji('🔐', "lock")
            self.add_emoji('⏩', "next")
            self.add_emoji('⏭️', "last")
        if self.autofooter == True:
            self.embeds[self.current_page].set_footer(text=self.embeds[self.current_page].footer.text + f' [{self.current_page+1}/{len(self.embeds)}]', icon_url=self.embeds[self.current_page].footer.icon_url)
        msg = await self.message.send(embed=self.embeds[self.current_page], content=self.embed_content)
        for emoji in self.control_emojis:
            await msg.add_reaction(emoji)
        msg = await msg.channel.fetch_message(msg.id)

        def check(reaction, user):
            return user == self.message.author and reaction.message.id == msg.id and str(
                reaction.emoji) in self.control_emojis
        while True:
            try:
                reaction, user = await self.bot.wait_for("reaction_add", check=check, timeout=self.timeout)
            except asyncio.TimeoutError:
                break

            for emoji in self.control_emojis:
                if emoji == str(reaction.emoji):
                    index = self.control_emojis.index(emoji)
                    cmd = self.control_commands[index]
                    if self.remove_reaction == True and msg.guild is not None:
                        await msg.remove_reaction(str(reaction.emoji), user)
                    if cmd.lower() == "first":
                        self.current_page = 0
                    elif cmd.lower() == "last":
                        self.current_page = len(self.embeds) - 1
                    elif cmd.lower() == "next":
                        self.current_page += 1
                        self.current_page = 0 if self.current_page > len(
                            self.embeds) - 1 else self.current_page
                    elif cmd.lower() == "back":
                        self.current_page = self.current_page - 1
                        self.current_page = len(
                            self.embeds) - 1 if self.current_page < 0 else self.current_page
                    elif cmd.lower() == "lock":
                        self.current_page = 0
                        await msg.clear_reactions()
                        return msg
                    if self.autofooter == True:
                        self.embeds[self.current_page].set_footer(text=(self.embeds[self.current_page].footer.text).replace(f" [{self.current_page+1}/{len(self.embeds)}]", "") + f' [{self.current_page+1}/{len(self.embeds)}]', icon_url=self.embeds[self.current_page].footer.icon_url)
                    await msg.edit(embed=self.embeds[self.current_page], content=self.embed_content)


class Embed:
    def __init__(self, bot):
        self.bot = bot

    async def music_help_embed(self, message):
        music_cmd = []
        for cmd in list(self.bot.all_commands):
            if str(self.bot.get_command(cmd).cog_name) == "Music":
                if str(cmd) == self.bot.get_command(cmd).name:
                    music_cmd.append(str(cmd))

        embeds = []
        for cmd in music_cmd:
            emb = await Utility.Client.command_help_embeds(self, message, cmd)
            embeds.append(emb[0])
        paginator = Paginator(self.bot, message, embeds, normal_emoji=True)
        await paginator.run()

    async def help_embed(self, message):
        helprandomcmd = []
        Category = {
            "Music": [],
            "Client": [],
            "Admin": [],
            "Utility": [],
            "Stats": [],
            "Fun": [],
            "Economy": [],
            "Season": [],
            "Moderation": [],
            "Dev": []
        }
        for cmd in list(self.bot.all_commands):
            if str(cmd) == self.bot.get_command(cmd).name:
                if str(self.bot.get_command(cmd).cog_name) in Category:
                    Category[str(self.bot.get_command(cmd).cog_name)].append(f"`{cmd}`")

        for i in range(2):
            cmd = self.bot.get_command(str(random.choice(list(self.bot.all_commands))))
            helprandomcmd.append(str(cmd.name))

        helpemb = discord.Embed(
            title=f"{Lenaimg} LENA BOT", color=0x1ab102, timestamp=datetime.datetime.utcnow())
        helpemb.add_field(
            name="\u200b", value=f"아래에는 레나봇의 모든 명령어가 보입니다.\n명령어 사용중 오류 발생시 **[Support Server](https://discord.gg/FTjCspj)**를 방문해주세요.", inline=False)
        helpemb.add_field(
            name="\u200b", value=f"**좋은 하루되세요!**", inline=False)
        helpemb.add_field(name=f"{Music_ICON} **MUSIC**",
                          value=f"`music`", inline=False)
        helpemb.add_field(name=f"{Client_ICON} **CLIENT**",
                          value=str.join(", ", Category['Client']), inline=False)
        helpemb.add_field(name=f"{Admin_ICON} **ADMIN**",
                          value=str.join(", ", Category['Admin']), inline=False)
        helpemb.add_field(name=f"{Util_ICON} **Utility**",
                          value=str.join(", ", Category['Utility']), inline=False)
        helpemb.add_field(name=f"{Stats_ICON} **STATS**",
                          value=str.join(", ", Category['Stats']), inline=False)
        helpemb.add_field(name=f"{FUN_ICON} **FUN**",
                          value=str.join(", ", Category['Fun']), inline=False)
        helpemb.add_field(name=f"{Economy_ICON} **Economy**",
                          value=str.join(", ", Category['Economy']), inline=False)
        helpemb.add_field(name=f"{SEASON_ICON} **SEASON**",
                          value=str.join(", ", Category['Season']), inline=False)
        helpemb.add_field(name=f"{Moder_ICON} **MODERATION**",
                          value=str.join(", ", Category['Moderation']), inline=False)
        helpemb.add_field(name=f"{Dev_ICON} **DEV**",
                          value=str.join(", ", Category['Dev']), inline=False)
        helpemb.add_field(
            name="\u200b", value=f"**레나와 대화를 하고싶다면? `레나야 [할말]`을 하시면 레나랑 대화할수 있습니다.**\n**명령어에 대한 자세한 도움말을 보시려면 `도움말 [명령어]`**", inline=False)
        helpemb.add_field(
            name="**Examples:**", value=f"`e!도움말 {helprandomcmd[0]}` **`{helprandomcmd[0]}`** 명령어에 대한 자세한 도움말을 볼수있습니다.\n`e!도움말 {helprandomcmd[1]}` **`{helprandomcmd[1]}`** 명령어에 대한 자세한 도움말을 볼수있습니다.", inline=False)
        helpemb.add_field(
            name="**Support:**", value=f"[Support Server](https://discord.gg/cGM4PcHvQq)\n[Invite me](http://lenabot.kro.kr)", inline=False)
        helpemb.set_footer(
            text=f"개발자: {self.bot.get_user(340124004599988234)}", icon_url=self.bot.get_user(340124004599988234).avatar_url)
        await message.send(embed=helpemb)

    async def lena_info_embed(self, message):
        cpu_info = cpuinfo.get_cpu_info()
        cpu = cpu_info['brand_raw']
        cpu_hz = (int(cpu_info['hz_actual'][0]) / 1000000000)
        ram_gb = int(round(psutil.virtual_memory().total / (1024.0 ** 3)))
        os = platform.system()
        os_ver = platform.version()
        emb = discord.Embed(
            description="안녕하세요!! 저는 **`레나`**봇 입니다. `관리`, `유틸`, `경제`, `대화`, `전적` 그 이외 기타 유용한 것을 제공합니다. (아님 말고요 ㅡ3ㅡ)", color=0x1ab102)
        emb.set_author(name=f"레나 | Lena", icon_url=self.bot.user.avatar_url)
        emb.add_field(name=f"시스템:", value=f"""
        {OS_ICON} **OS:** {os} `{os_ver}`
        {CPU_ICON} **CPU:** {cpu} `{cpu_hz} GHz`
        {RAM_ICON} **RAM:** {ram_gb} `(GB)`""", inline=False)
        emb.add_field(name="정보:", value=f"""
        {Dev_ICON} **개발자:** {self.bot.get_user(340124004599988234)}
        {VERSION_ICON} **버전:** {self.bot.__version__}
        {DISCORD_ICON} **공식 서버:** **[discord.gg/cGM4PcHvQq](https://discord.gg/cGM4PcHvQq)**""", inline=True)
        emb.add_field(name="통계:", value=f"""
        {SERVER_ICON} **서버:** `{format(len(self.bot.guilds), ',')}`
        {USER_ICON} **유저:** `{format(len(self.bot.users), ',')}`
        {CHANNEL_ICON} **채널:** `{format(len(set(self.bot.get_all_channels())), ',')}`""", inline=True)
        await message.send(embed=emb)

    def shard_info_embed(self):
        shard = self.bot.get_shard(list((self.bot.shards).keys())[0])
        process = psutil.Process()
        ram_usage = process.memory_info().rss / 1024 / 1024
        emb = discord.Embed(title=f"서버 샤드 정보", color=0x1ab102,
                            timestamp=datetime.datetime.utcnow())
        emb.description = f"""
# {shard.id}번 샤드 `(분리 시스템)`
```ml
# {shard.id} : Latency {shard.latency*1000:,.0f}ms, Ram {ram_usage:.2f}MB
```"""
        return emb

class Economy:
    def __init__(self, bot):
        self.bot = bot

    def create_data(self, user: discord.Member):
        with open('./data/User_Data/Economy/User_Data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        if str(user.id) not in data:
            data[str(user.id)] = {
                "money": 500,
                "debt": 0,
                "credit_rank": 4,
                "job_id": {
                    "main_id": 0,
                    "sub_id": 0
                },
                "job_time": 0
            }
            with open('./data/User_Data/Economy/User_Data.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)

    def load_data(self, user: discord.Member):
        Economy.create_data(self, user)
        with open('./data/User_Data/Economy/User_Data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data[str(user.id)]

    def job_load_data(self):
        with open('./data/User_Data/Economy/Job_Data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data

    def economy_profile_embed(self, message):
        data = Economy.load_data(self, message.author)
        jb_data = Economy.job_load_data(self)
        emb = discord.Embed(title=f"{Passbookimg}경제 정보", description=f"{message.author.mention}님의 경제 정보입니다.", color=self.bot.__color__, timestamp=datetime.datetime.utcnow())
        emb.add_field(name="**회원 이름:**", value=message.author)
        emb.add_field(name="**직업:**", value=jb_data[str(data["job_id"]["main_id"])][str(data["job_id"]["sub_id"])]["name"])
        return emb
    