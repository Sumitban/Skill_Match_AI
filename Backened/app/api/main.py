"""
FastAPI application for Skill Match AI resume screening system.
"""

from fastapi import FastAPI, HTTPException, status, UploadFile, File, Query
from typing import List
import uuid
import tempfile
import os

from Backened.app.config import get_config
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
from Backened.app.pipeline.candidate_service import CandidateService
from Backened.app.ranking.baseline_ranker import BaselineRanker
from Backened.app.ranking.feedback_service import FeedbackService
from Backened.app.storage.mongodb import Database
from Backened.app.exception.resume_exception import (
    ResumeExtractionError,
    ResumeFileNotFound
)
from Backened.app.utils.logger import logger


config = get_config()

app = FastAPI(
    title=config.APP_NAME,
    version=config.APP_VERSION,
    description="Automated resume screening and candidate ranking system.",
)

job_service = JobService()
candidate_service = CandidateService()
ranker = BaselineRanker()
feedback_service = FeedbackService()
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
            version=config.APP_VERSION
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

        job_id = str(uuid.uuid4())

        job = job_service.create_job(
            job_id,
            request.title,
            request.raw_text
        )

        return JobResponse(
            job_id=job["job_id"],
            title=job["title"]
        )

    except ValueError as e:

        raise HTTPException(status_code=409, detail=str(e))


# ============================================================
# Candidate Upload
# ============================================================

@app.post("/candidates/{job_id}", tags=["Candidates"])
async def upload_candidates(
    job_id: str,
    files: List[UploadFile] = File(...)
):

    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

    processed = 0
    failed = 0

    for file in files:

        if not file.filename.lower().endswith(".pdf"):
            failed += 1
            continue

        contents = await file.read()

        if len(contents) > MAX_FILE_SIZE:
            failed += 1
            continue

        try:

            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:

                tmp.write(contents)
                tmp_path = tmp.name

            candidate_service.process_candidate(job_id, tmp_path)

            os.remove(tmp_path)

            processed += 1

        except Exception as e:

            logger.error(f"Candidate processing failed: {e}")

            failed += 1

    return {
        "job_id": job_id,
        "processed": processed,
        "failed": failed
    }


# ============================================================
# Candidates (Pagination)
# ============================================================

@app.get("/candidates/{job_id}", response_model=CandidatesListResponse, tags=["Candidates"])
async def get_candidates(
    job_id: str,
    page: int = Query(1, ge=1),
    limit: int = Query(20, le=100)
):

    skip = (page - 1) * limit

    cursor = (
        db.candidates
        .find({"job_id": job_id}, {"_id": 1, "ranking": 1})
        .sort("ranking.rank_position", 1)
        .skip(skip)
        .limit(limit)
    )

    candidates = [

        CandidateDetail(
            _id=str(c["_id"]),
            ranking=c.get("ranking", {})
        )

        for c in cursor
    ]

    total = db.candidates.count_documents({"job_id": job_id})

    return CandidatesListResponse(
        job_id=job_id,
        candidates=candidates,
        count=total
    )


# ============================================================
# Ranking
# ============================================================

@app.post("/rank/{job_id}", response_model=RankingResponse, tags=["Ranking"])
async def rank_candidates(job_id: str):

    results = ranker.rank_candidates(job_id)

    return RankingResponse(
        job_id=job_id,
        count=len(results)
    )


# ============================================================
# Feedback
# ============================================================

@app.post("/feedback", response_model=FeedbackResponse, tags=["Feedback"])
async def submit_feedback(request: FeedbackRequest):

    feedback_service.update_hr_decision(
        request.candidate_id,
        request.decision
    )

    return FeedbackResponse(
        candidate_id=request.candidate_id
    )