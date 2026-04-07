"""
FastAPI application for Skill Match AI resume screening system.
"""

from fastapi import FastAPI, HTTPException, status, UploadFile, File, Query
from typing import List
import uuid
import tempfile
import os

from Backened.app.utils.logger import setup_logging, get_logger

from Backened.app.config import load_config
from Backened.app.api.schemas import (
    JobCreateRequest,
    FeedbackRequest,
    JobResponse,
    CandidateResponse,
    RankingResponse,
    FeedbackResponse,
    CandidatesListResponse,
    HealthResponse,
    CandidateDetail
)

from Backened.app.jobs.job_service import JobService
from Backened.app.file_pipeline.candidate_service import CandidateService
# from Backened.app.ranking.baseline_ranker import BaselineRanker
# from Backened.app.ranking.feedback_service import FeedbackService
from Backened.app.storage.mongodb import Database
from Backened.app.storage.candidate_repo import initialize_candidates_collection
from Backened.app.storage.jobs_repo import initialize_jobs_collection
from Backened.app.storage.file_repo import initialize_file_collection
from Backened.app.exception.resume_exception import (
    ResumeExtractionError,
    ResumeFileNotFound
)
from Backened.app.utils.logger import logger

config = load_config()

# Initialize MongoDb Collections and their Schemas
db = Database.get_db()

if "jobs" not in db.list_collection_names():
    initialize_jobs_collection(db)
    
if "candidates" not in db.list_collection_names():
    initialize_candidates_collection(db)
    
if "files" not in db.list_collection_names():
    initialize_file_collection(db)
    
# initial set up of logging
setup_logging()
logger.info("Logging is set up successfully.")
    

app = FastAPI(
    title=config["Setting"]["APP_NAME"],
    version=config["Setting"]["APP_VERSION"],
    description="Automated resume screening and candidate ranking system.",
)

job_service = JobService()
candidate_service = CandidateService()
# ranker = BaselineRanker()
# feedback_service = FeedbackService()
db = Database.get_db()


# ============================================================
# Health
# ============================================================

@app.get("/", response_model=HealthResponse, tags=["Health"])
async def health():

    try:
        Database.get_client().admin.command("ping")

        return HealthResponse(
            status="healthy",
            version = config["Setting"]["APP_VERSION"]
        )

    except Exception:

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection failed"
        )


# ============================================================
# Jobs
# ============================================================

@app.post("/jobs", response_model=JobResponse, status_code=201, tags=["Jobs"])
async def create_job(request: JobCreateRequest):

    try:
        logger.info("job is send for creation")
        job = job_service.create_job(
            request.title,
            request.raw_text
        )

        return JobResponse(
            job_id=job["job_id"],
            title=job["title"]
        )

    except ValueError as e:
        logger.err(f"bad json request : {e}")
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error : {e}")
        raise HTTPException(status_code=500, detail= str(e))


# ============================================================
# Candidate Upload
# ============================================================

@app.post("/candidates/{job_id}", tags=["Candidates"])
async def upload_candidates(
    job_id: str,
    files: List[UploadFile] = File(...)
):
    try:
        MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
        failed_files = []
        passed_files = []

        for file in files:

            if not file.filename.lower().endswith(".pdf"):
                failed_files.append({"name" : file.filename, "reason" : "Not a pdf"})
                continue
            
            if file.size > MAX_FILE_SIZE:
                failed_files.append({"name" : file.filename, "reason" : "Too Large"})
                continue
            
            passed_files.append(file)

        candidate_service.storage(passed_files, job_id = job_id)
        candidate_service.process_queue()

        return {
            "status": "Accepted",
            "job_id": job_id,
            "Summary": {
                "accepted_count": len(passed_files),
                "failed_count": len(failed_files),
                "faliures" : failed_files
            }
        }
    except Exception as e:
        logger.error(f"Error uploading candidates for job {job_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# # ============================================================
# # Candidates (Pagination)
# # ============================================================

# @app.get("/candidates/{job_id}", response_model=CandidatesListResponse, tags=["Candidates"])
# async def get_candidates(
#     job_id: str,
#     page: int = Query(1, ge=1),
#     limit: int = Query(20, le=100)
# ):

#     skip = (page - 1) * limit

#     cursor = (
#         db.candidates
#         .find({"job_id": job_id}, {"_id": 1, "ranking": 1})
#         .sort("ranking.rank_position", 1)
#         .skip(skip)
#         .limit(limit)
#     )

#     candidates = [

#         CandidateDetail(
#             _id=str(c["_id"]),
#             ranking=c.get("ranking", {})
#         )

#         for c in cursor
#     ]

#     total = db.candidates.count_documents({"job_id": job_id})

#     return CandidatesListResponse(
#         job_id=job_id,
#         candidates=candidates,
#         count=total
#     )


# # ============================================================
# # Ranking
# # ============================================================

# @app.post("/rank/{job_id}", response_model=RankingResponse, tags=["Ranking"])
# async def rank_candidates(job_id: str):

#     results = ranker.rank_candidates(job_id)

#     return RankingResponse(
#         job_id=job_id,
#         count=len(results)
#     )


# # ============================================================
# # Feedback
# # ============================================================

# @app.post("/feedback", response_model=FeedbackResponse, tags=["Feedback"])
# async def submit_feedback(request: FeedbackRequest):

#     feedback_service.update_hr_decision(
#         request.candidate_id,
#         request.decision
#     )
 
#     return FeedbackResponse(
#         candidate_id=request.candidate_id
#     )