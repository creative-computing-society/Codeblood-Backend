import discord
from discord import Role, Member, PermissionOverwrite
from discord.abc import Snowflake
from discord.ext import commands

import asyncio
from typing import Any, Dict, List, Union
from logging import getLogger

logger = getLogger(__name__)


class TeamChannels:
    def __init__(self, bot: commands.Bot) -> None:
        """
        While using this, just do this

        ```python
            team_channels = TeamChannels(bot)
        ```

        You need not define bot as its taking the bot from asyncio.create_tasks()
        """
        self.bot = bot
        self._invalid_ids = []

    @property
    def invalid_ids(self):
        """
        Returns all the ids that are invalid/not in guild.
        """

        return self._invalid_ids

    async def create_channels(self, teams: List[Dict[str, Any]]):
        """
        Just pass the entire teams collection to this
        """
        if not self.bot.guilds:
            raise RuntimeError("Bot is not in any guild")

        await self.bot.wait_until_ready()

        guild = self.bot.guilds[0]

        overwrites: Dict[Union[Role, Member, Snowflake], PermissionOverwrite] = {
            guild.default_role: PermissionOverwrite(view_channel=False),
        }

        for team in teams:
            member_id = None
            team_name: str = team["team_name"]
            players: List[Dict[str, Any]] = team["players"]

            for player in players:
                try:
                    member_id = int(player["discord_id"])
                    user = await self.bot.fetch_user(member_id)
                    overwrites[discord.Object(id=user.id)] = (
                        discord.PermissionOverwrite(view_channel=True)
                    )
                except discord.NotFound:
                    self._invalid_ids.append(member_id)

                except discord.HTTPException as e:
                    self._invalid_ids.append(member_id)
                    logger.error(f"Failed to fetch user {member_id}: {e}")

                except (ValueError, TypeError):
                    logger.error(
                        f"[!] Invalid Discord ID for player: {player.get('email')}"
                    )

            # Create category and 2 channels inside it
            category = await guild.create_category_channel(
                name=f"Team-{team_name.lower()}", overwrites=overwrites
            )

            await guild.create_text_channel(name="general", category=category)
            await guild.create_voice_channel(name="general", category=category)

        # Sleep to reset rate limit of discord
        await asyncio.sleep(1.5)
