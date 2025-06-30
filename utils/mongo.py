from typing import Dict, Any, cast
from dotenv import load_dotenv
from os import getenv

from pymongo import MongoClient
from pymongo.collection import Collection
from bson import ObjectId

load_dotenv()
MONGO_URI = getenv("MONGO_URI")


class MongoManager:
    def __init__(self) -> None:
        self.client = MongoClient(MONGO_URI)
        self.database = self.client.get_database("")

        assert self.client is not None, "Mongo URI is wrong"
        assert self.database is not None, "Mongo database not found"

    def get_teams(self) -> Collection[Dict[str, Any]]:
        return cast(Collection[Dict[str, Any]], self.database.get_collection("users"))

    def get_team(self, team_id: str) -> Dict[str, Any] | None:
        collection = self.get_teams()
        return collection.find_one({"team_id": team_id})

    def get_team_by_id(self, mongo_team_id: str) -> Dict[str, Any] | None:
        collection = self.get_teams()
        return collection.find_one({"_id": ObjectId(mongo_team_id)})

    def create_team(self):
        pass

    def get_lobby(self):
        pass

    def create_lobby(self):
        pass
