from os import getenv, listdir


def get_cogs(path: str, prefix: str):
    files = listdir(path)
    return [
        f"{prefix}.{f[:-3]}" for f in files if f.endswith(".py") and f != "__init__.py"
    ]


COGS = get_cogs("cogs", "cogs")
DISCORD_BOT_TOKEN = getenv("DISCORD_BOT_TOKEN")
