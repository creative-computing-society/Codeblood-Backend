import discord
from discord import Role, Member, PermissionOverwrite

from typing import Optional, Dict, Any, Union
from logging import getLogger

from database import teams
from views.utils import create_success_embed

logger = getLogger(__name__)
assert teams is not None, "Teams collection not found!"


class TeamChannelButton(discord.ui.View):
    def __init__(self, *, timeout: Optional[float] = 180):
        super().__init__(timeout=None)

    @discord.ui.button(
        custom_id="click_button",
        label="Click here",
        style=discord.ButtonStyle.primary,
        emoji="🏳️",
    )
    async def on_click(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if not interaction.guild:
            return

        guild = interaction.guild

        reg_view = discord.ui.View()
        reg_view.add_item(
            discord.ui.Button(
                style=discord.ButtonStyle.link,
                label="Register Now",
                emoji="🔗",
                url="https://obscura.ccstiet.com/",
            )
        )

        team: Dict[str, Any] | None = await teams.find_one(
            {
                "$or": [
                    {"players.discord_id": interaction.user.name.strip()},
                    {"players.discord_id": str(interaction.user.id)},
                ]
            }
        )

        if not team:
            embed = discord.Embed(
                color=discord.Color.red(),
                title="Team information not found!",
                description="Please make sure to register yourself for OBSCURA from the [OBSCURA registeration portal](https://obscura.ccstiet.com/).\n"
                + "If you have already registered, then most likely your Discord ID is wrong.\n"
                + "You can edit it on the team dashboard on the Registration Portal.",
            ).set_footer(text="If the issue percists, please contact CORE-25")

            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        voice_channel = discord.utils.get(
            interaction.guild.voice_channels, name=team["team_name"]
        )

        if not voice_channel:
            overwrites: Dict[
                Union[Role, Member, discord.Object], PermissionOverwrite
            ] = {
                interaction.guild.default_role: PermissionOverwrite(view_channel=False),
            }

            # Gets the Obscura category
            category = discord.utils.get(guild.categories, name="Obscura")

            if category is None:
                category_overwrites: Dict[
                    Union[Role, Member, discord.Object], PermissionOverwrite
                ] = {
                    guild.default_role: PermissionOverwrite(
                        view_channel=False, connect=False
                    ),
                }
                await guild.create_category(
                    name="Obscura", overwrites=category_overwrites
                )

            # Creates a voice channel
            await guild.create_voice_channel(
                name=team["team_name"], category=category, overwrites=overwrites
            )

        embed = create_success_embed(
            f"You have been added to team: {team['team_name']}. Please use the voice channel as your mode of communication."
        )
        await interaction.response.send_message(
            embed=embed, ephemeral=True, delete_after=3
        )
