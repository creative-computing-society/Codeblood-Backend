import discord
from discord.ext import commands
from discord.abc import PrivateChannel

import asyncio
from logging import getLogger
from os import path

from views import TeamChannelButton

logger = getLogger(__name__)
CATEGORY_NAME = "OBSCURA"

obscura_maze = discord.File(
    path.join("assets", "obscura_maze.jpg"), filename="obscura_maze.jpg"
)


class StartupMessages(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.join_channel_id = 1395877470590341290
        self.about_channel_id = 1395877004368281620
        self.rules_channel_id = 1395877379175485701

        asyncio.create_task(self._startup_send())

    # Creates the "Welcome to Obscura" message
    async def _startup_send(self) -> None:
        await self.bot.wait_until_ready()

        try:
            await asyncio.gather(
                self.send_about_event_message(),
                self.send_join_team_event_message(),
                self.send_rules_event_message(),
            )
        except Exception:
            logger.exception("Error in send_event_message")

    async def _validate(
        self, channel_id: int, channel_name
    ) -> discord.TextChannel | None:
        guild = self.bot.guilds[0]

        if not guild:
            logger.warning("Guild not found. Aborting message sending task.")
            return None

        channel = self.bot.get_channel(channel_id)

        if not channel:
            category = discord.utils.get(guild.categories, name=CATEGORY_NAME)
            channel = await guild.create_text_channel(channel_name, category=category)

        if not isinstance(channel, discord.TextChannel):
            logger.error("Channel must be a Text Channel!")
            return None

        return channel

    async def send_join_team_event_message(self):
        logger.info("Sending event message")

        channel = await self._validate(self.join_channel_id, "🚀・join-team-channel")

        if channel is None:
            return

        self.join_channel_id = channel.id
        channel = await self._validate(self.join_channel_id, "🚀・join-team-channel")

        if channel is None:
            return

        embed = discord.Embed(
            title="Welcome to Obscura!",
            description="To participate in the event, you need to join your team on Discord. You will be assignedto your team's voice channels. Click the button below to join your team.\n\n"
            + "Kindly ensure that your Discord username matches the one you provided during registration. Use the designated channels for all event-related communication. For any issues or assistance, feel free to contact any team officials. We hope you have an incredible experience! Have adventurous gameplay!",
            colour=discord.Color.red(),
        )

        embed.set_thumbnail(url="attachment://logo.png")
        embed.set_footer(text="Contact Core if you have any issues.")

        logo = discord.File(path.join("assets", "logo.png"), filename="logo.png")
        await channel.send(embed=embed, view=TeamChannelButton(), file=logo)

    async def send_about_event_message(self):
        logger.info("Sending about messsage")

        channel = await self._validate(self.about_channel_id, "🔎・about")

        if channel is None:
            return

        self.about_channel_id = channel.id

        channel = await self._validate(self.about_channel_id, "🔎・about")

        if channel is None:
            return

        embed = discord.Embed(
            description="[Welcome to Obscura](https://obscura.ccstiet.com/)\nObscura is a 4-player cooperative cyber-heist game set in a corrupted simulation of the TIET network. Players split into two roles — Hackers and Wizards — to tackle security puzzles, evade digital phantoms, and recover hidden data fragments. With each team navigating interconnected quadrants, success demands real-time coordination, logical thinking, and stealthy maneuvering.\n\n"
            + "Designed for thrill-seekers, puzzle-solvers, and strategy lovers alike, Obscura blends cryptic storytelling with immersive gameplay, promising an intense and unforgettable experience.",
            color=discord.Color.dark_blue(),
        ).set_image(url="attachment://obscura_maze.jpg")

        await channel.send(embed=embed, file=obscura_maze)

    async def send_rules_event_message(self):
        logger.info("sending rules message")

        channel = await self._validate(self.rules_channel_id, "📜・rules")

        if channel is None:
            return

        self.rules_channel_id = channel.id

        channel = await self._validate(self.rules_channel_id, "📜・rules")

        if channel is None:
            return

        embed = discord.Embed(
            title="📒 General Rules:",
            description=(
                "**1. Be Respectful**"
                "Treat all participants with respect and kindness. Harassment, hate speech, or discrimination of any form will not be tolerated.\n\n"
                "**2. No NSFW Content**"
                "Sharing explicit or inappropriate content is strictly prohibited.\n\n"
                "**3. No Spam**"
                "Avoid spamming the chat with repetitive messages, images, or links. Keep the discussions meaningful and relevant.\n\n"
                "**4. Use Channels Appropriately**"
                "Each channel has a specific purpose. Please ensure your discussions are relevant to the designated topics.\n\n"
                "**5. No Self-Promotion**"
                "Self-promotion or advertising your own content without prior permission from organizers is not allowed.\n\n"
                "**6. Report Issues**"
                "If you encounter any issues or witness rule violations, report them to the moderators promptly.\n\n"
                "**7. Maintain Dignity**"
                "Uphold the integrity and dignity of the game and all participants.\n\n"
                "**8. Report Offenses**"
                "If someone offends or annoys you, report the message to the CCS team and contact a Core. Provide proof, such as screenshots, so appropriate action can be taken. Do not engage in a flame war."
            ),
            color=discord.Color.dark_purple(),
        )

        embed.set_thumbnail(url="attachment://logo.png")

        logo = discord.File(path.join("assets", "logo.png"), filename="logo.png")
        await channel.send(embed=embed, file=logo)


async def setup(bot: commands.Bot):
    await bot.add_cog(StartupMessages(bot))
