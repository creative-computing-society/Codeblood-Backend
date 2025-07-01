from pymongo import MongoClient
from pymongo.collection import Collection

MONGO_DETAILS="mongodb://"
client= MongoClient(MONGO_DETAILS)
teams_db = client["team_database"]

teams_collection: Collection = teams_db["teams"]