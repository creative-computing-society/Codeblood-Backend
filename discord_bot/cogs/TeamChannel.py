from os import getenv
import discord
from discord.ext import commands, tasks

import asyncio
from typing import Any, Dict, Mapping
from logging import getLogger

from database import teams
from views import TeamChannelButton

logger = getLogger(__name__)

CATEGORY_NAME = "OBSCURA VOICE CHANNELS"
ADMIN_ROLE = getenv("ADMIN_ROLE")


assert teams is not None, "Teams collection not found!"
assert ADMIN_ROLE is not None, "Admin role not found!"


class TeamChannels(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self._invalid_ids = []
        self._not_in_guild = []
        self._creating = False

        self.bot.add_view(TeamChannelButton())

        self.auto_channel_creation.start()

    @property
    def invalid_ids(self):
        """
        Returns all the ids that are invalid/not in guild.
        """

        return self._invalid_ids

    @property
    def not_in_guild(self):
        return self._not_in_guild

    async def cog_unload(self):
        self.auto_channel_creation.cancel()

    @tasks.loop(minutes=5)
    async def auto_channel_creation(self):
        if self._creating:
            return

        self._creating = True
        await self.bot.wait_until_ready()

        guild = self.bot.guilds[0]
        all_teams = await teams.find({}).to_list(length=None)

        if not all_teams:
            logger.warning("No teams found in DB.")
            self._creating = False
            return

        for team in all_teams:
            await self._create_voice_channel(team, guild)
            await asyncio.sleep(1.5)

        logger.info("Voice channel sync complete.")
        self._creating = False

    # Get's each players discord id from db and edit perms accordingly
    async def resolve_player(self, player: Dict[str, Any], guild: discord.Guild):
        raw_id = player.get("discord_id", "").strip()
        member = None

        try:
            # Discord id is in the form of int, can use to check if id is valid or not
            if raw_id.isdigit():
                member_id = int(raw_id)

                member = guild.get_member(member_id)
                if not member:
                    try:
                        member = await guild.fetch_member(member_id)
                    except discord.NotFound:
                        self._not_in_guild.append(raw_id)
                        return None

            else:
                # Discord id is a string, cannot use to check if id is valid or not
                username_input = raw_id.lower()
                member = next(
                    (
                        m
                        for m in guild.members
                        if m.name.lower() == username_input
                        or (m.global_name and m.global_name.lower() == username_input)
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

    # Creates the voice channels and edit's their permission
    async def _create_voice_channel(self, team: Dict[str, Any], guild: discord.Guild):
        team_name: str = team["team_name"]
        players = team["players"]

        # Resolve members from DB
        resolved_members = await asyncio.gather(
            *[self.resolve_player(p, guild) for p in players]
        )
        resolved_members = list(filter(None, resolved_members))

        # Check if VC already exists
        normalized_team_name = team_name.strip().lower().replace(" ", "-")
        existing_channel = discord.utils.get(
            guild.voice_channels, name=normalized_team_name
        )

        if existing_channel:
            # Cleanup old permissions
            cleanup_tasks = [
                existing_channel.set_permissions(target, overwrite=None)
                for target in existing_channel.overwrites
                if isinstance(target, discord.Member) and target not in resolved_members
            ]
            update_tasks = [
                existing_channel.set_permissions(
                    member,
                    overwrite=discord.PermissionOverwrite(
                        view_channel=True, connect=True
                    ),
                )
                for member in resolved_members
            ]
            await asyncio.gather(*cleanup_tasks, *update_tasks)
            return

        # Build overwrites for team members
        overwrites: Mapping[Any, discord.PermissionOverwrite] = {
            guild.default_role: discord.PermissionOverwrite(
                view_channel=False, connect=False
            )
        }
        for member in resolved_members:
            overwrites[member] = discord.PermissionOverwrite(
                view_channel=True, connect=True
            )

        # Find a category with < 50 voice channels
        def get_or_create_category_slot(
            guild: discord.Guild, base_name: str = CATEGORY_NAME
        ):
            for category in guild.categories:
                if (
                    category.name.startswith(base_name)
                    and len(category.voice_channels) < 50
                ):
                    return category
            return None

        category = get_or_create_category_slot(guild)

        # If no suitable category, make a new one
        if category is None:
            count = sum(1 for c in guild.categories if c.name.startswith(CATEGORY_NAME))
            category = await guild.create_category(
                name=f"OBSCURA VOICE CHANNELS #{count + 1}",
                overwrites={
                    guild.default_role: discord.PermissionOverwrite(
                        view_channel=False, connect=False
                    )
                },
            )

        # Create VC
        await guild.create_voice_channel(
            name=normalized_team_name,
            category=category,
            overwrites=overwrites,
        )

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
    @commands.has_role(ADMIN_ROLE)
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

        reply_text = "Created voice channels, Here are the invalid IDs and the people who did not join this fucking discord server and made my blood boil"
        invalid_id_text = "\n".join(self._invalid_ids)
        not_in_guild_id_text = "\n".join(self._not_in_guild)

        if ctx.interaction:
            await ctx.interaction.followup.send(reply_text, ephemeral=True)
            await ctx.interaction.followup.send(invalid_id_text, ephemeral=True)
            await ctx.interaction.followup.send(not_in_guild_id_text, ephemeral=True)

        else:
            await ctx.reply(reply_text, ephemeral=True)
            await ctx.author.send(invalid_id_text)
            await ctx.author.send(not_in_guild_id_text)

        self._creating = False

    @commands.hybrid_command(name="delete_obscura_vcs")
    @commands.has_role(ADMIN_ROLE)
    async def delete_obscura_vcs(self, ctx: commands.Context):
        """
        Deletes all voice channels in categories starting with 'OBSCURA VOICE CHANNELS'.
        """
        guild = ctx.guild

        if not guild:
            logger.exception("Bot not in any guild!")
            return

        if not guild.categories:
            logger.exception("The fuck, no categories found??")
            return

        deleted = []

        # Filter categories that match
        target_categories = [
            category
            for category in guild.categories
            if category.name.startswith("OBSCURA VOICE CHANNELS")
        ]

        if not target_categories:
            await ctx.reply("No matching categories found.", ephemeral=True)
            return

        # Loop through each category and delete its voice channels
        for category in target_categories:
            for channel in category.voice_channels:
                try:
                    await channel.delete()
                    deleted.append(channel.name)
                    await asyncio.sleep(1)  # to avoid hitting rate limits
                except discord.HTTPException as e:
                    await ctx.send(f"Failed to delete {channel.name}: {e}")

        await ctx.reply(f"Deleted {len(deleted)} voice channels.", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(TeamChannels(bot))
