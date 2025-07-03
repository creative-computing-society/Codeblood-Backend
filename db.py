from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from os import getenv
from dotenv import load_dotenv
from logging import getLogger

logger = getLogger(__name__)

_db = None

load_dotenv()


def init_db():
    global _db

    uri = getenv("MONGO_URI", "mongodb://localhost:27017")
    if "localhost" in uri:
        logger.info("Connecting to local mongo DB")

    logger.info("Connecting to mongo db using uri")
    # Create a new client and connect to the server
    client = MongoClient(uri, server_api=ServerApi("1"))
    try:
        # Send a ping to confirm a successful connection
        client.admin.command("ping")
        logger.info("Pinged your deployment. You successfully connected to MongoDB!")
        _db = client
    except Exception as e:
        print(e)
        exit(1)


def get_db():
    global _db
    if _db is None:
        raise Exception("Why the fuck is db not initialized")
    return _db.get_database("data")
