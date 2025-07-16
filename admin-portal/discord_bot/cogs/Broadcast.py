import discord
from discord.ext import commands

from aiohttp import ClientSession
from logging import getLogger
from os import getenv

logger = getLogger(__name__)


class Broadcast(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.announcement_channel = int(getenv("ANNOUNCEMENT_CHANNEL"))
        self.post_url = "http://127.0.0.1:2130/test/"

        assert self.announcement_channel is not None, f"{self.announcement_channel}"

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

        await self.bot.process_commands(message)


async def setup(bot: commands.Bot):
    await bot.add_cog(Broadcast(bot))
    logger.info("Broadcast cog loaded")
