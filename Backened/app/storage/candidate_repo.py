from Backened.app.storage.mongodb import Database
from pymongo.errors import OperationFailure

my_schema = {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["job_id", "resume", "features", "ranking", "metadata"],
            "validationLevel": "strict",
            "validationAction": "error",
            "properties" : {
                "job_id": {
                    "bsonType": "string"
                },
                "resume": {
                    "bsonType": "object",
                    "required": ["raw_text", "skills", "years_experience"],
                    "properties": {
                        "raw_text": {"bsonType": "string"},
                        "skills": {
                            "bsonType": "array",
                            "items": {"bsonType": "string"}
                        },
                        "years_experience": {
                            "bsonType": ["int", "double"]
                        }
                    }
                },
                "github": {
                    "bsonType": "object"
                },
                "similarity": {
                    "bsonType": "object",
                    "properties": {
                        "resume_jd": {"bsonType": "double"},
                        "skills_jd": {"bsonType": "double"},
                        "github_jd": {"bsonType": "double"}
                    }
                },
                "features": {
                    "bsonType": "array",
                    "minItems": 9,
                    "maxItems": 9,
                    "items": {"bsonType": "double"}
                },
                "ranking": {
                    "bsonType": "object",
                    "properties": {
                        "prediction_score": {"bsonType": ["double", "null"]},
                        "hr_decision": {"bsonType": ["int", "null"]},
                        "rank_position": {"bsonType": ["int", "null"]}
                    }
                },
                "metadata": {
                    "bsonType": "object",
                    "required": ["created_at"],
                    "properties": {
                        "created_at": {"bsonType": "date"},
                        "updated_at": {"bsonType": ["date", "null"]},
                        "confidence_score": {"bsonType": "double"}
                    }
                }
            }
        }
    }

db = Database.get_db()

try:
    db.create_collection(
        "candidates",
        validator=my_schema
    )
except OperationFailure:
    pass  # Collection already exists

db.candidates.create_index("job_id")
db.candidates.create_index("ranking.prediction_score")
db.candidates.create_index("ranking.hr_decision")