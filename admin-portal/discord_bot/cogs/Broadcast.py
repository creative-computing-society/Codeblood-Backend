import discord
from discord.ext import commands

from aiohttp import ClientSession
from logging import getLogger
from os import getenv

logger = getLogger(__name__)


class Broadcast(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.announcement_channel = getenv("ANNOUNCEMENT_CHANNEL")
        self.post_url = "ask hari"

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.channel.id != self.announcement_channel or message.author.bot:
            return

        data = {
            "author": message.author.name,
            "content": message.content,
            "timestamp": str(message.created_at),
        }

        async with ClientSession() as session:
            try:
                async with session.post(self.post_url, json=data) as resp:
                    if resp.status != 200:
                        logger.error(f"POST failed: {resp.status}")
            except Exception as e:
                logger.error(f"Error posting message: {e}")


async def setup(bot: commands.Bot):
    await bot.add_cog(Broadcast(bot))
