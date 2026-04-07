from Backened.app.utils.logger import logger
from Backened.app.file_pipeline.storing_file import storing_file
from Backened.app.storage.mongodb import Database
from Backened.app.file_pipeline.queue import get_next_task
from Backened.app.pipeline.candidate_service import CandidateService as cs
import os
from pathlib import Path

class CandidateService:
    _run_ai_pipeline = None
    
    def __init__(self):
        self.db = Database.get_db()
        if self._run_ai_pipeline is None:
            self._run_ai_pipeline = cs()
            
    def storage(self, files, job_id):
        storing_file(job_id,files)
        
    def process_queue(self):
        while True:
            # 1. Grab one task safely
            task = get_next_task(self.db)
            if not task:
                break # Queue is empty
                
            try:
                # 2. Perform the heavy AI work
                file_path = task["file_path"]
                self._run_ai_pipeline.process_candidate(file_path, task["job_id"])
                
                # 3. Clean up: Delete File and Remove Task
                if os.path.exists(file_path):
                    os.remove(file_path)
                
                self.db.files.delete_one({"_id": task["_id"]})
                logger.info(f"Successfully processed {file_path}")

            except Exception as e:
                # 4. Error Handling: Reset status to pending so it can be retried
                logger.error(f"Failed task {task['_id']}: {e}")
                self.db.files.update_one(
                    {"_id": task["_id"]},
                    {"$set": {"status": "pending", "locked_at": None}}
                )
