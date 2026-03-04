"""
Baseline ranker module for scoring and ranking candidates.
Implements a weighted scoring algorithm based on feature vectors.
"""

from typing import List, Dict, Any
import numpy as np

from Backened.app.storage.mongodb import Database
from Backened.app.config import get_config
from Backened.app.utils.logger import logger

config = get_config()


class BaselineRanker:
    """Baseline ranker for scoring and ranking candidates based on feature vectors."""

    def __init__(self) -> None:
        """Initialize BaselineRanker with database connection."""
        self.db = Database.get_db()
        logger.info("BaselineRanker initialized")

    def normalize_years(
        self, 
        years: float, 
        max_years: int = config.MAX_YEARS_EXPERIENCE
    ) -> float:
        """
        Normalize years of experience to [0, 1] range.
        
        Caps experience at max_years to prevent dominance of this feature.
        
        Args:
            years: Number of years of experience
            max_years: Maximum years to cap normalization at (default: 10)
            
        Returns:
            Normalized value between 0 and 1
        """
        return min(years, max_years) / max_years

    def compute_score(self, feature_vector: np.ndarray) -> float:
        """
        Compute baseline compatibility score from feature vector.
        
        Feature index mapping:
            0: resume_jd_similarity (cosine similarity 0-1)
            1: skills_jd_similarity (cosine similarity 0-1)
            2: github_jd_similarity (cosine similarity 0-1)
            3: years_experience (numeric)
            4: skill_overlap (numeric count)
            5: repo_count (numeric count)
            6: star_count (numeric count)
            7: fork_ratio (numeric 0-1)
            8: language_match_score (numeric count)
        
        Args:
            feature_vector: Numpy array of candidate features
            
        Returns:
            Float score between 0 and 1
        """
        if len(feature_vector) < 4:
            logger.warning(f"Feature vector has insufficient features: {len(feature_vector)}")
            return 0.0

        resume_sim = float(feature_vector[0])
        skills_sim = float(feature_vector[1])
        github_sim = float(feature_vector[2])
        years_exp = float(feature_vector[3])

        normalized_years = self.normalize_years(years_exp)

        score = (
            config.WEIGHT_RESUME_SIM * resume_sim +
            config.WEIGHT_SKILLS_SIM * skills_sim +
            config.WEIGHT_GITHUB_SIM * github_sim +
            config.WEIGHT_YEARS_EXP * normalized_years
        )

        return float(score)

    def rank_candidates(self, job_id: str) -> List[Dict[str, Any]]:
        """
        Rank all candidates for a job using baseline scoring.
        
        Scores each candidate, assigns rank positions, and updates database.
        
        Args:
            job_id: Job identifier
            
        Returns:
            List of candidates with scores, sorted by score (descending)
            
        Raises:
            Exception: If database operations fail
        """
        logger.info(f"Starting ranking for job: {job_id}")
        
        try:
            candidates = list(
                self.db.candidates.find({"job_id": job_id})
            )

            if not candidates:
                logger.warning(f"No candidates found for job: {job_id}")
                return []

            logger.debug(f"Found {len(candidates)} candidates for job {job_id}")
            scored_candidates = []

            for candidate in candidates:
                try:
                    feature_vector = np.array(candidate["features"])
                    score = self.compute_score(feature_vector)

                    scored_candidates.append({
                        "candidate_id": candidate["_id"],
                        "score": score
                    })
                except (KeyError, ValueError) as e:
                    logger.warning(f"Error scoring candidate: {str(e)}")
                    continue

            # Sort descending by score
            scored_candidates.sort(
                key=lambda x: x["score"],
                reverse=True
            )

            # Assign rank position and update database
            logger.debug(f"Assigning ranks to {len(scored_candidates)} candidates")
            for rank, item in enumerate(scored_candidates, start=1):
                try:
                    self.db.candidates.update_one(
                        {"_id": item["candidate_id"]},
                        {
                            "$set": {
                                "ranking.prediction_score": item["score"],
                                "ranking.rank_position": rank
                            }
                        }
                    )
                except Exception as e:
                    logger.error(f"Error updating rank for candidate: {str(e)}")
                    continue

            logger.info(f"Ranking completed for job {job_id}: {len(scored_candidates)} candidates ranked")
            return scored_candidates
            
        except Exception as e:
            logger.error(f"Error ranking candidates for job {job_id}: {str(e)}")
            raise