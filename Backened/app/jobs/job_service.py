"""
Job service module for managing job postings and embeddings.
"""

from typing import Optional, Dict, Any
import numpy as np
import uuid
from datetime import datetime, timezone
from pymongo.errors import DuplicateKeyError

from Backened.app.storage.mongodb import Database
from Backened.app.embeddings.embedding_model import EmbeddingModel
from Backened.app.utils.logger import logger


class JobService:

    def __init__(self):
        self.db = Database.get_db()
        self.embedding_model = EmbeddingModel()
        logger.info("JobService initialized")

    # --------------------------------------------------
    # Create Job
    # --------------------------------------------------

    def create_job(
        self,
        title: str,
        raw_text: str
    ) -> Dict[str, Any]:

        if not raw_text.strip():
            logger.warning("Attempted to create job with empty description")
            raise ValueError("Job description cannot be empty")

        job_id = str(uuid.uuid4())

        try:

            embedding = self.embedding_model.encode(raw_text)

            if embedding is None:
                raise RuntimeError("Embedding generation failed")

            job_doc = {
                "job_id": job_id,
                "title": title,
                "raw_text": raw_text,
                "embedding": embedding.tolist(),
                "metadata": {
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": None
                }
            }

            self.db.jobs.insert_one(job_doc)
            logger.info(f"Job created: {job_id}")
            return job_doc

        except DuplicateKeyError:
            logger.warning(f"Duplicate job_id detected: {job_id}")
            raise ValueError("Duplicate job detected")
        except Exception as e:
            logger.error(f"Job creation failed: {str(e)}")
            raise

    # --------------------------------------------------
    # Get Job
    # --------------------------------------------------

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        job = self.db.jobs.find_one({"job_id": job_id})
        if not job:
            return None
        job["embedding"] = np.array(job["embedding"], dtype=float)
        return job

    # --------------------------------------------------
    # Update Job
    # --------------------------------------------------

    def update_job(self, job_id: str, new_raw_text: str) -> Dict[str, Any]:
        if not new_raw_text.strip():
            raise ValueError("Job description cannot be empty")

        new_embedding = self.embedding_model.encode(new_raw_text)

        result = self.db.jobs.update_one(
            {"job_id": job_id},
            {
                "$set": {
                    "raw_text": new_raw_text,
                    "embedding": new_embedding.tolist(),
                    "metadata.updated_at": datetime.now(timezone.utc)
                }
            }
        )
        if result.matched_count == 0:
            raise ValueError(f"Job with id '{job_id}' not found")

        return self.get_job(job_id)