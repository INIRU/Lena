import json
import os
import discord

from commands.etc import Utility
from discord.ext import commands, tasks

with open("./data/bot_config.json", "r", encoding="UTF-8") as f:
    data = json.load(f)


class LenaClient(commands.AutoShardedBot):
    __version__ = data['LenaClient']['version']
    __color__ = 0x1ab102

    def __init__(self):
        super().__init__(command_prefix=['#!'], case_insensitive=True,
                         owner_ids=[340124004599988234, 629908548637425690, 247305812123320321], description="LenaClient", chunk_guilds_at_startup=True, intents=discord.Intents.all())
        self.remove_command('help')

    def setup(self):
        Utility.Utility.load_cogs(self)

    def run(self):
        self.setup()

        print(f"{data['LenaClient']['name']} 봇을 구동합니다.")
        super().run(data["LenaClient"]["token"], bot=True, reconnect=True)

    async def on_ready(self):
        print(f"Connected to Discord (latency: {self.latency*1000:,.0f} ms).")
        print(f"Name: {self.user.name} | ID: {self.user.id}")

    async def on_shard_ready(self, shard_id):
        print(f"{shard_id}: Shard is ready!")


if __name__ == "__main__":
    LenaClient().run()
