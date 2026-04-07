from Backened.app.storage.mongodb import Database
from datetime import datetime, timezone
import uuid
import shutil

def storing_file(job_id: str, files: list):
    try:
        for file in files:
            # assigned task_id to the file
            task_id = str(uuid.uuid4())

            # path were raw files are stored
            storage_path = f"data/{task_id}.pdf"

            with open(storage_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            # database connection
            db = Database.get_db()

            file_detail = {
                "task_id": task_id,
                "job_id": job_id,
                "file_path": storage_path,
                "status": "pending",
                "attempts": 0,
                "created_at": datetime.now(timezone.utc)
            }

            db.files.insert_one(file_detail)
    except Exception as e:
        raise Exception(f"Error storing file: {str(e)}")
             
        
    