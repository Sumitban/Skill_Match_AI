import numpy as np
import re
import hashlib
from datetime import datetime

from Backened.app.storage.mongodb import Database
from Backened.app.ingestion.resume_ingestor import extract_text, extract_links
from Backened.app.ingestion.section_detector import extract_sections
from Backened.app.ingestion.section_confidence import compute_section_confidence

from Backened.app.github.github_client import GitHubClient
from Backened.app.github.github_features import (
    compute_repo_count,
    compute_star_count,
    compute_fork_ratio,
    compute_language_distribution,
    aggregate_readme_text
)

from Backened.app.features.feature_builder import FeatureBuilder
from Backened.app.embeddings.embedding_model import EmbeddingModel


class CandidateService:

    def __init__(self):
        self.db = Database.get_db()
        self.embedding_model = EmbeddingModel()
        self.feature_builder = FeatureBuilder(self.embedding_model)
        self.github_client = GitHubClient()

    def process_candidate(self, job_id: str, resume_path: str):

        job = self.db.jobs.find_one({"job_id": job_id})
        if not job:
            raise ValueError(f"Job with id {job_id} not found")

        jd_embedding = np.array(job["embedding"], dtype=float)
        jd_text = job["raw_text"]

        # Resume Parsing
        raw_text = extract_text(resume_path)
        links = extract_links(raw_text)
        sections = extract_sections(raw_text)

        confidence_score = compute_section_confidence(sections)

        # Resume hash for duplicate detection
        resume_hash = hashlib.sha256(raw_text.encode()).hexdigest()

        existing = self.db.candidates.find_one({
            "job_id": job_id,
            "resume_hash": resume_hash
        })

        if existing:
            return {
                "candidate_id": existing["_id"],
                "job_id": job_id
            }

        # Skills cleaning
        skills_raw = sections.get("skills", "")
        skills = [
            s.strip().lower()
            for s in re.split(r",|\n", skills_raw)
            if s.strip()
        ]

        resume_data = {
            "raw_text": raw_text,
            "sections": sections,
            "skills_text": skills_raw,
            "skills": skills,
            "years_experience": 0,
            "education": sections.get("education", ""),
            "links": links
        }

        # GitHub
        github_data = {
            "repo_count": 0,
            "total_stars": 0,
            "fork_ratio": 0.0,
            "language_distribution": {},
            "readme_text": ""
        }

        if links.get("github"):
            github_username = links["github"][0]

            try:
                repos = self.github_client.fetch_repositories(github_username)

                github_data = {
                    "username": github_username,
                    "repo_count": compute_repo_count(repos),
                    "total_stars": compute_star_count(repos),
                    "fork_ratio": compute_fork_ratio(repos),
                    "language_distribution": compute_language_distribution(repos),
                    "readme_text": aggregate_readme_text(
                        self.github_client,
                        github_username,
                        repos
                    )
                }

            except Exception:
                repos = []

        # Feature Building
        feature_vector = self.feature_builder.build_feature_vector(
            resume_data,
            github_data,
            jd_embedding,
            jd_text
        )

        resume_sim, skills_sim, github_sim = feature_vector[:3]

        candidate_doc = {

            "job_id": job_id,
            "resume_hash": resume_hash,

            "resume": resume_data,
            "github": github_data,

            "similarity": {
                "resume_jd": float(resume_sim),
                "skills_jd": float(skills_sim),
                "github_jd": float(github_sim)
            },

            "features": feature_vector.tolist(),

            "ranking": {
                "prediction_score": None,
                "hr_decision": None,
                "rank_position": None
            },

            "metadata": {
                "created_at": datetime.utcnow(),
                "updated_at": None,
                "confidence_score": float(confidence_score)
            }
        }

        result = self.db.candidates.insert_one(candidate_doc)

        return {
            "candidate_id": result.inserted_id,
            "job_id": job_id
        }