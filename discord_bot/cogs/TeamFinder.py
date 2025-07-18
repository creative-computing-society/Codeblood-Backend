import discord
from discord.ext import commands


class LookingForTeamView(discord.ui.View):
    def __init__(self, player_id):
        super().__init__()
        self.player_id = player_id
        self.selected_role = None

    @discord.ui.select(
        placeholder="Which role are you going to play?",
        options=[
            discord.SelectOption(label="💻 Hacker", value="hacker"),
            discord.SelectOption(label="🧙 Wizard", value="wizard"),
        ],
    )
    async def select_role(
        self, interaction: discord.Interaction, select: discord.ui.Select
    ):
        if interaction.user.id != self.player_id:
            await interaction.response.send_message(
                "This isn't your LFT panel.", ephemeral=True
            )
            return

        self.selected_role = select.values[0]

        # Create embed
        embed = discord.Embed(
            title="Player Looking for Team",
            description=f"{interaction.user.mention} is looking for a team as `{self.selected_role.capitalize()}`",
            color=discord.Color.green(),
        )

        # Add Accept Button
        accept_button = discord.ui.Button(
            label="Invite to Team", style=discord.ButtonStyle.success
        )

        async def accept_callback(btn_interaction: discord.Interaction):
            if btn_interaction.user.id == self.player_id:
                await btn_interaction.response.send_message(
                    "You can't invite yourself to your own team!", ephemeral=True
                )
                return

            await btn_interaction.response.send_message(
                f"{btn_interaction.user.mention} has invited {interaction.user.mention} to their team!",
                ephemeral=False,
            )

        accept_button.callback = accept_callback

        # Send embed with button
        view = discord.ui.View()
        view.add_item(accept_button)
        await interaction.channel.send(embed=embed, view=view)
        await interaction.response.send_message(
            f"You've been marked as LFT as a {self.selected_role.capitalize()}!",
            ephemeral=True,
        )


class TeamFinder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command("team-finder")
    async def lft(self, ctx):
        """Mark yourself as Looking For Team (LFT)"""
        view = LookingForTeamView(ctx.author.id)
        await ctx.send("Select your role:", view=view, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(TeamFinder(bot))
