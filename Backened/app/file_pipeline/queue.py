from datetime import datetime, timezone
from pymongo import ReturnDocument

def get_next_task(db):
    return db.files.find_one_and_update(
        filter={
            "status": "pending",
            "attempts": {"$lt": 3} # Don't retry forever if it crashes
        },
        update={
            "$set": {
                "status": "processing",
                "locked_at": datetime.now(timezone.utc)
            },
            "$inc": {"attempts": 1}
        },
        sort=[("created_at", 1)], # Oldest first (FIFO)
        return_document=ReturnDocument.AFTER
    )
