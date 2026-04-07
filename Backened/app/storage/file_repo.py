from pymongo.errors import OperationFailure

file_schema = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["task_id", "job_id", "file_path"],
            "validationLevel": "strict",
            "validationAction": "error",
            "properties" : {
                "task_id": {
                    "bsonType": "string"
                },
                "job_id": {
                    "bsonType": "string"
                },
                "file_path": {
                    "bsonType": "string"
                },
                "status": {
                    "bsonType": ["pending", "complete"]
                },
                "attempts": {
                    "bsonType": "int"
                },
                "created_at": {
                    "bsonType": "date"
                }
            }
        }
    }

def initialize_file_collection(db):
    try:
        db.create_collection(
            "files",
            validator=file_schema,
            validationLevel = "strict",
            validationAction = "error"
        )
        db.candidates.create_index("task_id")
    except OperationFailure:
        pass  # Collection already exists

