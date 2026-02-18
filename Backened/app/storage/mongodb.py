from pymongo import MongoClient, errors
from utils.logger import logger

url = "mongodb://localhost:27017/"
database_name = "skill_match_AI"

class database():
    _client : MongoClient = None
    
    @classmethod
    def get_client(cls):
        try:
            if cls._client is None:
                cls._client = MongoClient(
                    url,
                    serverSelectionTimeoutMS = 5000,
                    connectionTimeoutMS = 10000
                )

            #checking is the connection made or not
            cls._client.admin.command('ping')
            return cls._client
        except errors.ServerSelectionTimeoutError as e:
            logger.error(f"could not connect to Mongodb: Server Selection Timeout, {e}")
            raise
        except errors.ConnectionFailure as e:
            logger.critical(f"Mongodb connection faliure: {e}")
            raise
        except Exception as e:
            logger.critical(f"An unexpected error occured : {e}")
            exit(1)
            
    @classmethod
    def get_db(cls):
        client = cls.get_client()
        existing_dbs = client.list_database_names()
        if database_name not in existing_dbs:
            logger.warning(f"There is no existing database: {database_name}")
        return client[database_name]
        
            
    @classmethod
    def close_client(cls):
        if cls._client:
            cls._client.close()
            cls._client = None
            logger.info("Mongodb connection close")
