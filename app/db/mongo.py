from pymongo import MongoClient
from os import getenv
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)

db = client["data"]
sessions_col = db["sessions"]
users_col = db["users"]
sockets_col = db["socket_ids"]
teams_col = db["teams"]

phase1_db = client["phase1_event"]

nations_col = db["nations"]
sockets_col = db["socket_ids"]
