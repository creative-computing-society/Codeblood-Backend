import discord
from discord import app_commands
from discord.ext import commands

from typing import Optional, Type, Any
from dotenv import load_dotenv
from logging import getLogger
from asyncio import create_task

from .utils import COGS, DISCORD_BOT_TOKEN

load_dotenv()

logger = getLogger(__name__)

if COGS is None or DISCORD_BOT_TOKEN is None:
    raise RuntimeError("COGS/ Discord bot token is/are empty")


class Bot(commands.Bot):
    def __init__(
        self,
        command_prefix,
        *,
        tree_cls: Type[app_commands.CommandTree[Any]] = app_commands.CommandTree,
        description: Optional[str] = None,
        intents: discord.Intents,
        **options: Any,
    ) -> None:
        super().__init__(
            command_prefix,
            tree_cls=tree_cls,
            description=description,
            intents=intents,
            **options,
        )
        self.initial_extensions = COGS

    # Lazy Loads every cog in the cogs directory
    async def setup_hook(self):
        for extension in self.initial_extensions:
            try:
                await self.load_extension(extension)
            except Exception as e:
                logger.error(f"Error loading extension {extension}: {e}")

    async def on_ready(self):
        logger.info("Bot is Up and ready!")
        try:
            synced = await self.tree.sync()
            logger.info(f"Synced {len(synced)} command(s)")

        except Exception as e:
            logger.error(e)

        await self.change_presence(
            activity=discord.Game(name="Hypixel API shitting"),
            status=discord.Status.dnd,
        )


def bot():
    intents = discord.Intents.default()
    intents.members = True  # required to fetch member info
    intents.guilds = True

    bot = Bot(command_prefix="!", intents=intents)

    create_task(bot.start(DISCORD_BOT_TOKEN))
