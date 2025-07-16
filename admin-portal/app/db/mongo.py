from motor.motor_asyncio import AsyncIOMotorClient
from os import getenv
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = getenv("MONGO_URI", "mongodb://localhost:27017")

client = AsyncIOMotorClient(MONGO_URI)
db = client["obscura"]  # directly specify the DB name here

# Define collections
users_col = db["users"]
teams_col = db["teams"]
mail_sent_col = db["mail_sent"]