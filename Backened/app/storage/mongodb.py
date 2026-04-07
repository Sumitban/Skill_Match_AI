from pymongo import MongoClient, errors
from Backened.app.config import load_config
from Backened.app.utils.logger import get_logger
    
config = load_config()

MONGO_URL = config["Database"]["MONGO_URL"]
DATABASE_NAME = config["Database"]["DATABASE_NAME"]
MONGO_TIMEOUT_MS = config["Database"]["MONGO_TIMEOUT_MS"]
MONGO_CONNECT_TIMEOUT_MS = config["Database"]["MONGO_CONNECT_TIMEOUT_MS"]

logger = get_logger("storage")

class Database:
    _client: MongoClient = None

    @classmethod
    def get_client(cls):
        try:
            if cls._client is None:
                cls._client = MongoClient(
                    MONGO_URL,
                    serverSelectionTimeoutMS= MONGO_TIMEOUT_MS,
                    connectTimeoutMS= MONGO_CONNECT_TIMEOUT_MS
                )

            cls._client.admin.command("ping")
            return cls._client

        except errors.ServerSelectionTimeoutError as e:
            logger.error(f"Could not connect to MongoDB: {e}")
            raise

        except errors.ConnectionFailure as e:
            logger.critical(f"MongoDB connection failure: {e}")
            raise

    @classmethod
    def get_db(cls):
        client = cls.get_client()
        return client[DATABASE_NAME]

    @classmethod
    def close_client(cls):
        if cls._client:
            cls._client.close()
            cls._client = None
            logger.info("MongoDB connection closed")