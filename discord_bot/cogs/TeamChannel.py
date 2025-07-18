import discord
from discord import Role, Member, PermissionOverwrite
from discord.abc import PrivateChannel
from discord.ext import commands

import asyncio
from typing import Any, Dict, Mapping, Union, Optional
from logging import getLogger

from database import teams

logger = getLogger(__name__)
CATEGORY_NAME = "OBSCURA"

assert teams is not None, "Teams collection not found!"


class TeamChannels(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.channel_id = 1395448700985413642
        self._invalid_ids = []
        self._creating = False

        self.bot.add_view(TeamChannelButton())
        asyncio.create_task(self._startup_send())

    @property
    def invalid_ids(self):
        """
        Returns all the ids that are invalid/not in guild.
        """

        return self._invalid_ids

    async def _startup_send(self) -> None:
        # 1) don’t do anything until discord.py has populated cache
        await self.bot.wait_until_ready()

        # 2) run your actual send_event_message, catching errors
        try:
            await self.send_event_message()
        except Exception:
            logger.exception("Error in send_event_message")

    async def _create_voice_channel(self, team: Dict[str, Any], guild: discord.Guild):
        overwrites: Mapping[Any, discord.PermissionOverwrite] = {
            guild.default_role: discord.PermissionOverwrite(
                view_channel=False, connect=False
            ),
        }

        team_name = team["team_name"]
        players = team["players"]

        async def resolve_player(player: Dict[str, Any]):
            raw_id = player.get("discord_id", "").strip()
            member = None

            try:
                if raw_id.isdigit():
                    member_id = int(raw_id)

                    member = guild.get_member(member_id)
                    if not member:
                        try:
                            member = await guild.fetch_member(member_id)
                        except discord.NotFound:
                            self._invalid_ids.append(raw_id)
                            return None

                else:
                    username_input = raw_id.lower()
                    member = next(
                        (
                            m
                            for m in guild.members
                            if m.name.lower() == username_input
                            or (
                                m.global_name
                                and m.global_name.lower() == username_input
                            )
                        ),
                        None,
                    )
                    if not member:
                        self._invalid_ids.append(raw_id)
                        return None

                # Final check: validate user exists
                try:
                    await self.bot.fetch_user(member.id)
                except discord.NotFound:
                    self._invalid_ids.append(raw_id)
                    return None

                return member

            except (discord.HTTPException, ValueError, TypeError) as e:
                self._invalid_ids.append(raw_id)
                return None

        resolved_members = await asyncio.gather(*[resolve_player(p) for p in players])

        for member in filter(None, resolved_members):
            overwrites[member] = discord.PermissionOverwrite(
                view_channel=True, connect=True
            )

        # Get/create category
        category = discord.utils.get(guild.categories, name="Obscura")
        if not category:
            category = await guild.create_category(
                name="Obscura",
                overwrites={
                    guild.default_role: discord.PermissionOverwrite(
                        view_channel=False, connect=False
                    )
                },
            )

        await guild.create_voice_channel(
            name=team_name, category=category, overwrites=overwrites
        )

    async def send_event_message(self):
        logger.info("Sending event message")

        guild = self.bot.guilds[0]

        if not guild:
            logger.warning("Guild not found. Aborting on_ready task.")
            return

        channel = self.bot.get_channel(self.channel_id)

        if not channel:
            category = discord.utils.get(guild.categories, name=CATEGORY_NAME)
            channel = await guild.create_text_channel(CATEGORY_NAME, category=category)

        if isinstance(
            channel, (discord.ForumChannel, PrivateChannel, discord.CategoryChannel)
        ):
            logger.error("Channel must be a Text Channel!")
            return

        embed = discord.Embed(
            title="Welcome to Syrinx! Pixels In Pursuit",
            description="To participate in the event, you need to join your team on Discord. You will be assigned a role to access your team's channels. Click the button below to join your team.\n\n"
            + "Kindly ensure that your Discord username matches the one you provided during registration. Use the designated channels for all event-related communication. For any issues or assistance, feel free to contact any team officials. We hope you have an incredible experience! Have adventurous gameplay!",
            colour=discord.Color.red(),
        )

        embed.set_thumbnail(url="https://syrinx.ccstiet.com/logo.png")
        embed.set_footer(text="Contact Core if you have any issues.")

        await channel.send(embed=embed, view=TeamChannelButton())

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        team: Dict[str, Any] | None = await teams.find_one(
            {
                "$or": [
                    {"players.discord_id": member.name.strip()},
                    {"players.discord_id": str(member.id)},
                ]
            }
        )

        if team is None:
            logger.warning("Team not found or user is a bot!")
            return

        guild = self.bot.guilds[0]
        voice_channel = discord.utils.get(guild.voice_channels, name=team["team_name"])

        if voice_channel is None:
            await self._create_voice_channel(team, guild)
        else:
            # Set permission for the user
            overwrite = discord.PermissionOverwrite()
            overwrite.view_channel = True
            overwrite.connect = True
            await voice_channel.set_permissions(member, overwrite=overwrite)

    @commands.hybrid_command(name="create-vcs")
    @commands.has_role("CORE")
    async def create_channels(self, ctx: commands.Context):
        """
        Just pass the entire teams collection to this
        """

        if self._creating:
            return

        if ctx.interaction:
            await ctx.interaction.response.defer(ephemeral=True)

        if not self.bot.guilds:
            raise RuntimeError("Bot is not in any guild")

        self._creating = True

        # Waits till bot is running
        await self.bot.wait_until_ready()

        # Gets the discord server
        guild = self.bot.guilds[0]

        all_teams = await teams.find({}).to_list(length=None)

        assert all_teams is not None, (
            "Either someone nuked teams colelction or teams collection not found"
        )

        for team in all_teams:
            await self._create_voice_channel(team, guild)

            # Sleep to reset rate limit of discord
            await asyncio.sleep(1.5)

        reply_text = "Created voice channels, DM-ing you the invalid IDs"
        dm_text = " ".join(self._invalid_ids)

        if ctx.interaction:
            await ctx.interaction.followup.send(reply_text, ephemeral=True)
            await ctx.interaction.followup.send(dm_text, ephemeral=True)
        else:
            await ctx.reply(reply_text, ephemeral=True)
            await ctx.author.send(dm_text)
        self._creating = False


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
                url="https://syrinx.ccstiet.com/",
            )
        )

        team: Dict[str, Any] | None = await teams.find_one(
            {
                "%or": [
                    {"players.discord_id": interaction.user.name.strip()},
                    {"players.discord_id": str(interaction.user.id)},
                ]
            }
        )

        if not team:
            await interaction.response.send_message(
                "Team information not found! Please make sure to register yourself for OBSCURA from the OBSCURA portal",
                ephemeral=True,
            )
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

        await interaction.response.send_message(
            f"You have been added to team: {team['team_name']}. Please use this as your mode of communication.",
            ephemeral=True,
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(TeamChannels(bot))
