"""
API request and response schemas for Skill Match AI.
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


# ============================================================
# Request Models
# ============================================================

class JobCreateRequest(BaseModel):
    """
    Request schema for creating a job.
    Job ID is generated internally using UUID.
    """

    title: str = Field(..., min_length=3, max_length=200)
    raw_text: str = Field(..., min_length=50)


class FeedbackRequest(BaseModel):
    """
    HR decision on a candidate.
    """

    candidate_id: str
    decision: int = Field(..., ge=0, le=1)


# ============================================================
# Response Models
# ============================================================

class JobResponse(BaseModel):

    job_id: str
    title: str
    message: str = "Job created successfully"


class CandidateResponse(BaseModel):

    candidate_id: str
    job_id: str
    message: str = "Candidate processed successfully"


class RankingResponse(BaseModel):

    job_id: str
    count: int
    message: str = "Ranking complete"


class FeedbackResponse(BaseModel):

    candidate_id: str
    message: str = "Feedback recorded successfully"


# ============================================================
# Candidate Listing
# ============================================================

class RankingInfo(BaseModel):

    prediction_score: Optional[float] = None
    rank_position: Optional[int] = None


class CandidateDetail(BaseModel):

    id: str = Field(..., alias="_id")
    ranking: RankingInfo

    class Config:
        populate_by_name = True


class CandidatesListResponse(BaseModel):

    job_id: str
    page: int
    limit: int
    total: int
    candidates: List[CandidateDetail]


# ============================================================
# Health
# ============================================================

class HealthResponse(BaseModel):

    status: str = "healthy"
    version: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)