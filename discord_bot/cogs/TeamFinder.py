from discord.ext import commands

from database import teams
from views import LookingForTeamView
from views.utils import create_failure_embed

from logging import getLogger

logger = getLogger(__name__)
assert teams is not None, "Teams collection is None!"


class TeamFinder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command("team-finder")
    async def lft(self, ctx: commands.Context):
        if ctx.channel.id != 1395877818570903622:
            embed = create_failure_embed(
                "You can only run this command in 🤝・find-teammates-here!",
                title="Permission Denied",
            )
            await ctx.send(embed=embed)
            return

        view = LookingForTeamView(ctx.author.id)
        await ctx.send("Select your role:", view=view, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(TeamFinder(bot))
