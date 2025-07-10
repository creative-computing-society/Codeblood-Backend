from app.database.database import MongoManager

from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from typing import Optional

database: Optional[AsyncIOMotorDatabase] = None
users: Optional[AsyncIOMotorCollection] = None
lobbies: Optional[AsyncIOMotorCollection] = None
teams: Optional[AsyncIOMotorCollection] = None


async def init_db():
    global database
    mongo = await MongoManager.create()
    database = mongo.databases


async def init_users():
    global users
    assert database is not None, "Datavase not initialized properly!"

    users = database.get_collection("users")

    assert users is not None, "Users collection not found!"
    await users.create_index("email", unique=True)


async def init_lobbies():
    global lobbies
    assert database is not None, "Datavase not initialized properly!"

    lobbies = database.get_collection("lobbies")

    # TODO: Add an index to lobbies if possible


async def init_teams():
    global teams
    assert database is not None, "Datavase not initialized properly!"

    teams = database.get_collection("teams")

    # NOTE: Adding indexes is kinda addictive ngl
    await teams.create_index("team_name", unique=True)
    await teams.create_index("team_code", unique=True)
