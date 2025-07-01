from pymongo import MongoClient
from os import getenv
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)

db = client["phase1_event"]

users_col = db["users"]
sessions_col = db["sessions"]
teams_col = db["teams"]
nations_col = db["nations"]
sockets_col = db["socket_ids"]