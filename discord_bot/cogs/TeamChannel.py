from os import getenv
import discord
from discord.abc import PrivateChannel
from discord.ext import commands, tasks

import asyncio
from typing import Any, Dict, Mapping
from logging import getLogger

from database import teams
from views import TeamChannelButton

logger = getLogger(__name__)

CATEGORY_NAME = "OBSCURA"
ADMIN_ROLE = getenv("ADMIN_ROLE")

assert teams is not None, "Teams collection not found!"
assert ADMIN_ROLE is not None, "Admin role not found!"


class TeamChannels(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.channel_id = 1395448700985413642
        self._invalid_ids = []
        self._not_in_guild = []
        self._creating = False

        self.bot.add_view(TeamChannelButton())
        asyncio.create_task(self._startup_send())

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

    # Creates the "Welcome to Obscura" message
    async def _startup_send(self) -> None:
        await self.bot.wait_until_ready()

        try:
            await self.send_event_message()
        except Exception:
            logger.exception("Error in send_event_message")

    @tasks.loop(minutes=15)
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
        overwrites: Mapping[Any, discord.PermissionOverwrite] = {
            guild.default_role: discord.PermissionOverwrite(
                view_channel=False, connect=False
            ),
        }

        team_name = team["team_name"]
        players = team["players"]

        # Gets the members in parallel cause I love async coding
        resolved_members = await asyncio.gather(
            *[self.resolve_player(p, guild) for p in players]
        )

        # Makes the overwrites according to each memeber
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

        # ❗ Check if voice channel already exists
        existing_channel = discord.utils.get(category.voice_channels, name=team_name)

        if existing_channel:
            return

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
            title="Welcome to Obscura!",
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


async def setup(bot: commands.Bot):
    await bot.add_cog(TeamChannels(bot))
