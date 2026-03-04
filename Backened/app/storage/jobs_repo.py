
from Backened.app.storage.mongodb import Database
from pymongo.errors import OperationFailure

db = Database.get_db()

try:
    db.create_collection(
        "jobs",
        validator={
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["job_id", "raw_text", "embedding", "metadata"],
                "properties": {
                    "job_id": {"bsonType": "string"},
                    "title": {"bsonType": "string"},
                    "raw_text": {"bsonType": "string"},
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
        },
        validationLevel="strict",
        validationAction="error"
    )
except OperationFailure:
    pass  # Collection already exists

db.jobs.create_index("job_id", unique=True)