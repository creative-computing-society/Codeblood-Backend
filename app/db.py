from pymongo import MongoClient
from os import getenv
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)

db = client.get_database("data")
token_sessions = db["sessions"]
users = db["users"]
socket_connections = db["socket_ids"]
teams = db["teams"]
