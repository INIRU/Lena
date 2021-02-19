# pylint: disable=relative-beyond-top-level

import wavelink
import discord
import typing
import re
import random
import datetime
import asyncio
import math
import json
import async_timeout

from discord.ext import commands, tasks
from ..etc import CmdError, Utility

URL_REGEX = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
OPTIONS = {
    "1️⃣": 0,
    "2⃣": 1,
    "3⃣": 2,
    "4⃣": 3,
    "5⃣": 4,
}
with open("./data/bot_config.json", "r", encoding="UTF-8") as f:
    data = json.load(f)
Musicimg = data["LenaClient"]["emoji"]["Music"]


class Track(wavelink.Track):
    __slots__ = ('requester', 'request_channel', )

    def __init__(self, *args, **kwargs):
        super().__init__(*args)

        self.requester = kwargs.get('requester')
        self.request_channel = kwargs.get('request_channel')

class Queue:
    def __init__(self):
        self._queue = []
        self.position = 0
        self.repeat = False

    @property
    def is_empty(self):
        return not self._queue

    @property
    def is_pos(self):
        return self.position

    @property
    def current_track(self):
        if not self._queue:
            raise CmdError.Music.Empty_Queue

        if self.position <= len(self._queue) - 1:
            return self._queue[self.position]

    @property
    def upcoming(self):
        if not self._queue:
            raise CmdError.Music.Empty_Queue

        return self._queue[self.position + 1:]

    @property
    def history(self):
        if not self._queue:
            raise CmdError.Music.Empty_Queue

        return self._queue[:self.position]

    @property
    def length(self):
        return len(self._queue)

    @property
    def next_track(self):
        if not self._queue:
            raise CmdError.Music.Empty_Queue

        if self.position <= len(self._queue) - 1:
            return self._queue[self.position + 1]

    @property
    def por_track(self):
        if not self._queue:
            raise CmdError.Music.Empty_Queue

        if self.position <= len(self._queue) - 1:
            return self._queue[self.position - 1]

    @property
    def Queue_List(self):
        if not self._queue:
            raise CmdError.Music.Empty_Queue

        return self._queue

    @property
    def Get_Repeat(self):
        return self.repeat

    def add(self, *args):
        self._queue.extend(args)

    def get_next_track(self):
        if not self._queue:
            raise CmdError.Music.Empty_Queue

        self.position += 1

        if self.position < 0:
            return None
        elif self.position > len(self._queue) - 1:
            if self.repeat == True:
                self.position = 0
            else:
                return None

        return self._queue[self.position]

    def shuffle(self):
        if not self._queue:
            raise CmdError.Music.Empty_Queue

        upcoming = self.upcoming
        random.shuffle(upcoming)
        self._queue = self._queue[:self.position + 1]
        self._queue.extend(upcoming)

    def set_repeat(self):
        if self.repeat == True:
            self.repeat = False
            return self.repeat
        elif self.repeat == False:
            self.repeat = True
            return self.repeat

    def empty(self):
        self._queue.clear()
        self.position = 0

class Player(wavelink.Player):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queue = Queue()

        self.stop_votes = set()
        self.skip_votes = set()
        self.previous_votes = set()

    async def connect(self, ctx, channel=None):
        if (channel := getattr(ctx.author.voice, "channel", channel)) is None:
            raise CmdError.Music.NoVoiceChannel

        await super().connect(channel.id)
        return channel

    async def teardown(self):
        try:
            self.skip_votes.clear()
            self.previous_votes.clear()
            self.stop_votes.clear()

            await self.destroy()
        except KeyError:
            pass

    async def add_tracks(self, message, tracks, search: bool):
        if not tracks:
            raise CmdError.Music.TrackNotfound

        if isinstance(tracks, wavelink.TrackPlaylist):
            if (track := await self._track(message, tracks, True, False)) is not None:
                for track in tracks.tracks:
                    self.queue.add(Track(track.id, track.info, requester=message.author, request_channel=message.channel.id))
        else:
            if (track := await self._track(message, tracks, False, search)) is not None:
                track = Track(track.id, track.info, requester=message.author, request_channel=message.channel.id)
                self.queue.add(track)

        if not self.is_playing and not self.queue.is_empty:
            await self.start_playback()

    async def _track(self, message, tracks, Playlist: bool, search: bool):
        emb = discord.Embed(color=self.bot.__color__)
        if Playlist == False:
            if search == False:
                if tracks[0].is_stream == True:
                    length = "🔴 라이브"
                elif tracks[0].is_stream == False:
                    length = Utility.Utility.get_duration(
                        self, tracks[0].length//1000)
                emb.title = f"{Musicimg} 트랙에 추가됨! - {length}"
                emb.description = f"**[{tracks[0].title}]({tracks[0].uri})**"
                emb.timestamp = datetime.datetime.utcnow()
                emb.set_footer(text=message.author, icon_url=message.author.avatar_url)
                await message.send(embed=emb)
                return tracks[0]
            elif search == True:
                def _check(r, u):
                    return (
                        r.emoji in OPTIONS.keys()
                        and u == message.author
                        and r.message.id == msg.id
                    )
                emb = discord.Embed(colour=self.bot.__color__,
                                    timestamp=datetime.datetime.utcnow())
                emb.description = (
                    "\n".join(
                        f"`{i+1}.` **[{t.title}]({t.uri})**"
                        for i, t in enumerate(tracks[:5])
                    )
                )
                msg = await message.send(embed=emb)
                for emoji in list(OPTIONS.keys())[:min(len(tracks), len(OPTIONS))]:
                    await msg.add_reaction(emoji)

                try:
                    reaction, _ = await self.bot.wait_for("reaction_add", timeout=60.0, check=_check)
                except asyncio.TimeoutError:
                    await msg.delete()
                else:
                    await msg.clear_reactions()
                    length = Utility.Utility.get_duration(
                        self, tracks[OPTIONS[reaction.emoji]].length//1000)
                    emb.title = f"{Musicimg} 트랙에 추가됨! - {length}"
                    emb.description = f"**[{tracks[OPTIONS[reaction.emoji]].title}]({tracks[OPTIONS[reaction.emoji]].uri})**"
                    emb.timestamp = datetime.datetime.utcnow()
                    emb.set_footer(text=message.author,
                                   icon_url=message.author.avatar_url)
                    await msg.edit(embed=emb)
                    return tracks[OPTIONS[reaction.emoji]]
        elif Playlist == True:
            pl_length = 0
            for t in tracks.tracks:
                pl_length += t.length
            length = Utility.Utility.get_duration(self, pl_length//1000)
            emb.title = f"{Musicimg} 트랙에 추가됨! - {length}"
            emb.description = f"**[{tracks.tracks[0].title}]({tracks.tracks[0].uri})** 그 외 **`{len(tracks.tracks) - 1}`** 트랙"
            emb.timestamp = datetime.datetime.utcnow()
            emb.set_footer(text=message.author,
                           icon_url=message.author.avatar_url)
            await message.send(embed=emb)
            return tracks

    async def start_playback(self):
        await self.play(self.queue.current_track)

    async def do_next(self):
        if self.is_playing:
            return

        try:
            if (track := self.queue.get_next_track()) is not None:
                self.skip_votes.clear()
                self.previous_votes.clear()
                self.stop_votes.clear()
                await self.play(track)
            else:
                await self.teardown()
        except CmdError.Music.Empty_Queue:
            pass

    async def repeat_track(self):
        await self.play(self.queue.current_track)


class Music(commands.Cog, wavelink.WavelinkMixin, name="Music"):
    def __init__(self, bot):
        self.bot = bot
        self.wavelink = wavelink.Client(bot=bot)
        self.bot.loop.create_task(self.start_nodes())

    def cog_unload(self):
        self.wavelink.nodes.clear()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.id == self.bot.user.id and after.channel == None:
            return await self.get_player(member.guild).teardown()
        if member and (int(before.channel.id) if before.channel is not None else 1) != (int(after.channel.id) if after.channel is not None else 2) and self.get_player(member.guild):
            try:
                with async_timeout.timeout(30):
                    try: 
                        while not [m for m in self.bot.get_channel(int(self.get_player(member.guild).channel_id)).members if not m.bot]:
                            await asyncio.sleep(0.1)
                    except:
                        return await self.get_player(member.guild).teardown()
            except asyncio.TimeoutError:
                return await self.get_player(member.guild).teardown()

    async def cog_before_invoke(self, message):
        guild_check = message.guild is not None

        if guild_check:
            await self.ensure_voice(message)
        return guild_check

    def required(self, message):
        player = self.get_player(message)
        i = 0
        for m in self.bot.get_channel(player.channel_id).members:
            if not m.bot:
                i += 1
        required = math.ceil(i / 2.5)
        return required

    def is_privileged(self, message):
        player = self.get_player(message)

        return player.queue.current_track.requester == message.author or message.author.guild_permissions.administrator

    async def ensure_voice(self, message):
        player = self.get_player(message)

        if not message.author.voice or not message.author.voice.channel:
            raise CmdError.Music.NoVoiceChannel
        should_connect = message.command.name in ('재생', '검색', '들어와')

        if not message.author.voice or not message.author.voice.channel:
            raise CmdError.Music.NoVoiceChannel

        if not player.is_connected:
            if should_connect:
                await player.connect(message)
        else:
            if int(player.channel_id) != message.author.voice.channel.id:
                raise CmdError.Music.AlreadyConnectedToChannel(str(player.channel_id))

    @wavelink.WavelinkMixin.listener()
    async def on_node_ready(self, node):
        print(f"""WaveLink Node Link:
IP: {node.host}:{node.port}
REGION: {node.region}
IDENTIFIER: {node.identifier}
""")

    @wavelink.WavelinkMixin.listener("on_track_stuck")
    @wavelink.WavelinkMixin.listener("on_track_end")
    @wavelink.WavelinkMixin.listener("on_track_exception")
    async def on_player_stop(self, node, payload):
        await payload.player.do_next()

    async def start_nodes(self):
        await self.bot.wait_until_ready()

        nodes = {
            "MAIN": {
                "host": "127.0.0.1",
                "port": 2333,
                "rest_uri": "http://127.0.0.1:2333",
                "password": "OHruElsa123@@",
                "identifier": "LENACLIENT",
                "region": "ko",
            }
        }

        for node in nodes.values():
            await self.wavelink.initiate_node(**node)

    def get_player(self, obj):
        if isinstance(obj, commands.Context):
            return self.wavelink.get_player(obj.guild.id, cls=Player, context=obj)
        elif isinstance(obj, discord.Guild):
            return self.wavelink.get_player(obj.id, cls=Player)

    @commands.command(name="들어와", aliases=["join", "connect", "ct"])
    @commands.guild_only()
    async def _connect(self, message, *, channel: typing.Optional[discord.VoiceChannel]):
        await message.message.add_reaction("👌")

    @commands.command(name="나가", aliases=["disconnect", "leave", "dc"])
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def _disconnect(self, message):
        player = self.get_player(message)
        await player.teardown()
        await message.message.add_reaction("👋")

    @commands.command(name="재생", aliases=["play", "p", "ㅔ"])
    @commands.guild_only()
    async def _play(self, message, *, query: typing.Optional[str]):
        player = self.get_player(message)

        if query is None:
            if player.queue.is_empty:
                raise CmdError.Music.Empty_Queue

            await message.invoke(self.bot.get_command('재개'))

        else:
            query = query.strip("<>")
            if not re.match(URL_REGEX, query):
                query = f"ytsearch:{query}"

            await player.add_tracks(message, await self.wavelink.get_tracks(query), False)

    @commands.command(name="검색", aliases=["search", "srch", "srp"])
    @commands.guild_only()
    async def _search(self, message, *, query: typing.Optional[str]):
        player = self.get_player(message)

        if query is None:
            if player.queue.is_empty:
                raise CmdError.Music.Empty_Queue

        else:
            query = query.strip("<>")
            if not re.match(URL_REGEX, query):
                query = f"ytsearch:{query}"

            await player.add_tracks(message, await self.wavelink.get_tracks(query), True)

    @commands.command(name="일시정지", aliases=["pause"])
    @commands.guild_only()
    async def _pause(self, message):
        player = self.get_player(message)

        if not player.is_playing:
            raise CmdError.Music.Not_playing

        if player.is_paused:
            raise CmdError.Music.PlayerIsAlreadyPaused

        if not self.is_privileged(message):
            raise CmdError.Music.Not_Requster

        await player.set_pause(True)
        await message.message.add_reaction("👌")
        await message.send(f"{message.author.mention}, 일시정지를 해제하라면 **`play, resume`**명령어를 입력해주세요.")

    @commands.command(name="재개", aliases=["resume"])
    @commands.guild_only()
    async def _resume(self, message):
        player = self.get_player(message)

        if not player.is_playing:
            raise CmdError.Music.Not_playing

        if not player.is_paused:
            raise CmdError.Music.PlayerIsAlreadyResumed

        if not self.is_privileged(message):
            raise CmdError.Music.Not_Requster

        await player.set_pause(False)
        await message.message.add_reaction("👌")

    @commands.command(name="스킵", aliases=["skip", "sk", "sp", "next", "nt", "다음곡"])
    @commands.guild_only()
    async def _skip(self, message):
        player = self.get_player(message)

        if not player.queue.upcoming:
            raise CmdError.Music.NoMoreTracks

        if not self.is_privileged(message):
            required = self.required(message)
            player.skip_votes.add(message.author)
            if not len(player.skip_votes) >= required:
                return await message.send(f"{message.author.mention}, **`{message.command}`** 명령어의 투표를 진행하였습니다. **`[{len(player.skip_votes)} / {required}]`**")

        await player.stop()
        emb = discord.Embed(color=self.bot.__color__)
        emb.title = f"{Musicimg} 다음곡 - {Utility.Utility.get_duration(self, player.queue.next_track.length//1000)}"
        emb.description = f"**[{player.queue.next_track.title}]({player.queue.next_track.uri})**"
        emb.set_footer(text=message.author, icon_url=message.author.avatar_url)
        await message.send(embed=emb)

    @commands.command(name="이전곡", aliases=["previous", "pvios"])
    @commands.guild_only()
    async def _previous(self, message):
        player = self.get_player(message)

        if not player.queue.history:
            raise CmdError.Music.NoPreviousTracks

        if not self.is_privileged(message):
            required = self.required(message)
            player.previous_votes.add(message.author)
            if not len(player.previous_votes) >= required:
                return await message.send(f"{message.author.mention}, **`{message.command}`** 명령어의 투표를 진행하였습니다. **`[{len(player.previous_votes)} / {required}]`**")

        player.queue.position -= 2
        await player.stop()
        emb = discord.Embed(color=self.bot.__color__)
        emb.title = f"{Musicimg} 이전곡 - {Utility.Utility.get_duration(self, player.queue.por_track.length//1000)}"
        emb.description = f"**[{player.queue.por_track.title}]({player.queue.por_track.uri})**"
        emb.set_footer(text=message.author, icon_url=message.author.avatar_url)
        await message.send(embed=emb)

    @commands.command(name="믹서", aliases=["shuffle", "sfle"])
    @commands.guild_only()
    async def _shuffle(self, message):
        player = self.get_player(message)
        player.queue.shuffle()
        await message.send(f"{message.author.mention}, 재생목록에 있는 음악들을 썩었습니다.")

    @commands.command(name="반복", aliases=["loop", "lp", "repeat"])
    @commands.guild_only()
    async def repeat_command(self, message):
        player = self.get_player(message)

        if not self.is_privileged(message):
            raise CmdError.Music.Not_Requster

        player.queue.set_repeat()
        typs = "꺼짐"
        if player.queue.Get_Repeat == True:
            typs = "켜짐"
        await message.send(f"🔁 **반복 모드:** {typs}")

    @commands.command(name="재생목록", aliases=["queue", "que"])
    @commands.guild_only()
    async def _queue(self, message, page: typing.Optional[int] = 1):
        player = self.get_player(message)

        if player.queue.is_empty:
            raise CmdError.Music.Empty_Queue

        if page < 0:
            return await message.send(f"{message.author.mention}, **`0`**보다 큰 수를 입력하여주세요.")

        start = player.queue.is_pos + 1
        dec = ""
        embeds = []
        if player.queue.upcoming:
            alllength = 0
            for index, track in enumerate(player.queue.Queue_List[start:]):
                if track.is_stream == False:
                    length = Utility.Utility.get_duration(
                        self, track.length//1000)
                    alllength += track.length
                else:
                    length = "🔴 라이브"
                if len(str(dec).split("\n")) == 11:
                    emb = discord.Embed(colour=self.bot.__color__)
                    emb.description = dec
                    emb.set_footer(text=message.author, icon_url=message.author.avatar_url)
                    embeds.append(emb)
                    dec = ""
                dec += str(f'`{index + 1}.` `[{length}]` **[{track.title}]({track.uri})**\n')
            emb = discord.Embed(colour=self.bot.__color__)
            emb.description = dec
            emb.set_footer(text=message.author, icon_url=message.author.avatar_url)
            embeds.append(emb)
            text = f"▶ **{player.queue.current_track.title}**\n{Musicimg} 재생목록 | {len(player.queue.Queue_List[start:])} 트랙 | `{Utility.Utility.get_duration(self, alllength//1000)}`" + (
                " | 🔁" if player.queue.Get_Repeat == True else "")
            paginator = Utility.Paginator(self.bot, message, embeds, normal_emoji=True, autofooter=True, embed_content=text, current_page=page - 1)
            await paginator.run()
        else:
            await message.invoke(self.bot.get_command('지금곡'))

    @commands.command(name="비우기", aliases=["queueclear", "qc", "queclear", "stop"])
    @commands.guild_only()
    async def _clear(self, message):
        player = self.get_player(message)

        if player.queue.is_empty:
            raise CmdError.Music_QueueEmpty

        if not self.is_privileged(message):
            required = self.required(message)
            player.stop_votes.add(message.author)
            if not len(player.stop_votes) >= required:
                return await message.send(f"{message.author.mention}, **`{message.command}`** 명령어의 투표를 진행하였습니다. **`[{len(player.stop_votes)} / {required}]`**")

        player.queue.empty()
        await player.stop()
        await message.send(f"{message.author.mention}, 재생목록을 비웠습니다.")

    @commands.command(name="지금곡", aliases=["nowsong", "nowplaying", "np", "재생곡"])
    @commands.guild_only()
    async def _nowplaying(self, message):
        player = self.get_player(message)

        emb = discord.Embed(color=self.bot.__color__)
        if player.queue.current_track.is_stream == True and emb.description == discord.Embed.Empty:
            length = "🔴 라이브"
            bar = "▶ ▬▬▬▬▬▬▬▬▬▬🔘"
            emb.description = f"**[{player.queue.current_track.title}]({player.queue.current_track.uri})**\n{bar} `[{length}]`"
        elif player.queue.current_track.is_stream == False and emb.description == discord.Embed.Empty:
            length = player.queue.current_track.length//1000
            pos = player.position//1000
            barfull = int("%.0f" % (int(pos) / int(length) * 10))
            base = list("▬▬▬▬▬▬▬▬▬▬▬")
            base[barfull] = "🔘"
            bar = "".join(base)
            emb.description = f"**[{player.queue.current_track.title}]({player.queue.current_track.uri})**\n▶ {bar} `[{Utility.Utility.get_duration(self, int(pos))}/{Utility.Utility.get_duration(self, int(length))}]` 🔊\n"

        emb.set_thumbnail(url=player.queue.current_track.thumb)
        emb.set_author(name=player.queue.current_track.requester, icon_url=player.queue.current_track.requester.avatar_url)
        emb.timestamp = datetime.datetime.utcnow()
        await message.send(embed=emb)

    @commands.command(name="시간스킵", aliases=["m", "move", "seek"])
    @commands.guild_only()
    async def _seek(self, message, *, seconds: int):
        player = self.get_player(message)

        if not player.is_playing:
            raise CmdError.Music.Not_playing

        if not self.is_privileged(message):
            raise CmdError.Music.Not_Requster

        if player.queue.current_track.is_stream == True:
            raise CmdError.Music.Not_Seek_Live

        length = player.queue.current_track.length//1000
        pos = (player.position + (seconds * 1000))//1000
        barfull = int("%.0f" % (int(pos) / int(length) * 10))
        base = list("▬▬▬▬▬▬▬▬▬▬▬")
        base[barfull] = "🔘"
        bar = "".join(base)
        emb = discord.Embed(color=0x1ab102, description=f"""
            **[{player.queue.current_track.title}]({player.queue.current_track.uri})**
            ▶ {bar} `[{Utility.Utility.get_duration(self, int(pos))}/{Utility.Utility.get_duration(self, int(length))}]` 🔊
            """)
        emb.set_thumbnail(url=player.queue.current_track.thumb)
        emb.set_author(name=message.author, icon_url=message.author.avatar_url)
        emb.timestamp = datetime.datetime.utcnow()
        await message.send(embed=emb)
        track_time = player.position + (seconds * 1000)
        await player.seek(track_time)


def setup(bot):
    bot.add_cog(Music(bot))