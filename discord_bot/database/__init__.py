from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection

from .database import MongoManager

database: Optional[AsyncIOMotorDatabase] = None
teams: Optional[AsyncIOMotorCollection] = None


async def init_db():
    global database
    mongo = await MongoManager.create()
    database = mongo.databases


async def init_teams():
    global teams
    assert database is not None, "Datavase not initialized properly!"

    teams = database.get_collection("teams")

    # NOTE: Adding indexes is kinda addictive ngl
    await teams.create_index("team_name", unique=True)
    await teams.create_index("team_code", unique=True)
