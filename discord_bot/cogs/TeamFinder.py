import discord
from discord.ext import commands

from database import teams
from views import LookingForTeamView

import aiosqlite
from logging import getLogger

logger = getLogger(__name__)
assert teams is not None, "Teams collection is None!"


class TeamFinder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command("team-finder")
    async def lft(self, ctx):
        async with aiosqlite.connect("lft.db") as db:
            cursor = await db.execute(
                "SELECT 1 FROM lft_users WHERE discord_id = ?", (ctx.author.id,)
            )
            exists = await cursor.fetchone()

            if exists:
                embed = discord.Embed(
                    color=discord.Color.red(),
                    description="You're already marked as Looking For Team!",
                ).set_footer(text="Contact CORE if this is a mistake!")
                await ctx.send(embed=embed, ephemeral=True)
                return

            await db.execute(
                "INSERT INTO lft_users (discord_id) VALUES (?)", (ctx.author.id,)
            )
            await db.commit()

        view = LookingForTeamView(ctx.author.id)
        await ctx.send("Select your role:", view=view, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(TeamFinder(bot))
