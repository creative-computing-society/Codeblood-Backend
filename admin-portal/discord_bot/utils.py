from os import listdir
from dotenv import load_dotenv

load_dotenv()


def get_cogs(path: str, prefix: str):
    files = listdir(path)
    return [
        f"{prefix}.{f[:-3]}" for f in files if f.endswith(".py") and f != "__init__.py"
    ]


COGS = get_cogs("discord_bot/cogs", "discord_bot.cogs")
