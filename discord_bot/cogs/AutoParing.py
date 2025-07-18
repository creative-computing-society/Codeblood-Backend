from discord.ext import commands

import asyncio
from logging import getLogger
from database import teams

logger = getLogger(__name__)
assert teams is not None, "Teams collection is None!"


class AutoPairing(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = teams

    def pair_teams_linear(self, teams_iterable):
        size_buckets = {1: [], 2: [], 3: []}
        for team in teams_iterable:
            n = len(team["players"])
            if 1 <= n <= 3:
                size_buckets[n].append(team)

        result = []

        # Pair 2 + 2
        twos = size_buckets[2]
        while len(twos) >= 2:
            result.append((twos.pop(), twos.pop()))

        # Pair 3 + 1
        ones, threes = size_buckets[1], size_buckets[3]
        while ones and threes:
            result.append((ones.pop(), threes.pop()))

        return result

    @commands.hybrid_command(description="Auto pair teams so that total players = 4")
    @commands.has_role("CORE")
    async def autopair_bulk(self, ctx):
        await ctx.defer()
        cursor = self.db.find({}).batch_size(200)

        # Collect into list as we stream
        teams = [team async for team in cursor]

        # Off‑load CPU work
        paired = await asyncio.to_thread(self.pair_teams_linear, teams)

        if not paired:
            return await ctx.send("No valid pairs found.")

        lines = [
            f"✅ `{a['team_name']}` ({len(a['players'])}) + "
            f"`{b['team_name']}` ({len(b['players'])})"
            for a, b in paired
        ]
        await ctx.send("**Paired Teams:**\n" + "\n".join(lines))


async def setup(bot):
    await bot.add_cog(AutoPairing(bot))
