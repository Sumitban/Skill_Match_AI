
from pymongo.errors import OperationFailure
from Backened.app.storage.mongodb import Database
from Backened.app.utils.logger import get_logger

logger = get_logger("storage")

class JobRepository:
    
    job_schema = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["job_id", "raw_text", "embedding", "metadata"],
        "properties": {
            "job_id": {"bsonType": "string"},
            "title": {"bsonType": "string"},
            "raw_text": {
                "bsonType": "string",
                "minLength": 50
                },
            "embedding": {
                "bsonType": "array",
                "items": {"bsonType": "double"}
            },
            "metadata": {
                "bsonType": "object",
                "required": ["created_at"],
                "properties": {
                    "created_at": {"bsonType": "date"},
                    "updated_at": {"bsonType": ["date", "null"]}
                }
            }
        }
    }
    }
    
    def __init__(self):
        self.db = Database.get_db()
        if not self.db.list_collection_names().__contains__("jobs"):
            self._ensure_collection()
        self.collection = self.db["jobs"]
        
    def _ensure_collection(self)-> None:
        try: 
            self.db.create_collection(
                "jobs",
                validator= JobRepository.job_schema,
                validationLevel= "strict",
                validationAction= "error"
                )
            self.db.jobs.create_index("job_id", unique=True)
            
            logger.info("Jobs collection created and indexed successfully.")
        except OperationFailure:
            pass # Collection already exists
    
    def get_jobs(self)-> dict:
        try:
            logger.info("fetching all jobs")
            return list(self.collection.find({}, {"_id": 0, "job_id": 1, "title": 1}))        
        except Exception as e:
            logger.warning("Unable to fetch the records from the jobs collection")
            raise ("unknown exception") from e

    def get_job_by_id(self, job_id: str)-> dict:
        try:
            logger.info(f"fetch the specific record of {job_id}")
            return self.collection.find_one({"job_id": job_id}, {"_id": 0})
        except Exception as e:
            logger.warning(f"Unable to fetch the record for job_id: {job_id}")
            raise ("unknown exception") from e
    
    def insert_job(self, job_data: dict)-> str:
        try:
            result = self.collection.insert_one(job_data)
            logger.info(f"job is inserted successfully with the job_Id : {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            logger.warning("job is not inserted")
            raise ("unknown exception") from e
