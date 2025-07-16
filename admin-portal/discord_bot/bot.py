import discord
from discord.ext import commands
from discord_bot.handlers import setup_team_channels
from dotenv import load_dotenv
import os

load_dotenv()

intents = discord.Intents.default()
intents.members = True  # required to fetch member info
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f"🤖 Logged in as {bot.user}")

@bot.command(name="sync-discord")
@commands.has_role("CORE")
async def sync_discord(ctx):
    await ctx.send("Syncing Discord with team database...")

    # Core channel setup logic
    await setup_team_channels(ctx.guild)

    await ctx.send("✅ Sync Complete!")

bot.run(os.getenv("DISCORD_TOKEN"))