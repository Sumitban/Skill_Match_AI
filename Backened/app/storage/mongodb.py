from pymongo import MongoClient, errors
import os
from Backened.app.utils.logger import logger

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017/")
DATABASE_NAME = os.getenv("DATABASE_NAME", "skill_match_AI")


class Database:
    _client: MongoClient = None

    @classmethod
    def get_client(cls):
        try:
            if cls._client is None:
                cls._client = MongoClient(
                    MONGO_URL,
                    serverSelectionTimeoutMS=5000,
                    connectTimeoutMS=10000
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