import discord
from typing import Optional


def create_success_embed(message: str, title: Optional[str] = None):
    embed = discord.Embed(color=discord.Color.green(), description=message, title=title)
    return embed


def create_failure_embed(message: str, title: Optional[str] = None):
    embed = discord.Embed(color=discord.Color.red(), description=message, title=title)
    return embed
