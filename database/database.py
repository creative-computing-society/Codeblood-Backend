from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from dotenv import load_dotenv
from os import getenv
from logging import getLogger

load_dotenv()

logger = getLogger(__name__)

LOCALHOST_MONGO = "mongodb://localhost:27017"
MONGO_URI = getenv("MONGO_URI", LOCALHOST_MONGO)


# Mainly made this to annoy Hari >:) (no hate on you Hari, I just like to annoy people :))
class MongoManager:
    def __init__(self, client: AsyncIOMotorClient) -> None:
        self.client = client
        self._database = self.client.get_database("obscura")

    @classmethod
    async def create(cls):
        client = AsyncIOMotorClient(MONGO_URI)
        try:
            await client.admin.command("ping")
            if MONGO_URI == LOCALHOST_MONGO:
                logger.info("Connected to localhost mongo!")
            logger.info("Connected to Mongo using URI")
        except Exception as e:
            logger.error(f"Mongo connection failed! {e}")
        return cls(client)

    @property
    def databases(self) -> AsyncIOMotorDatabase:
        return self._database
