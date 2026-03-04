"""
Feedback service module for recording HR decisions on candidates.
Manages the collection of labeled data for model training.
"""

from typing import Union
from bson import ObjectId

from Backened.app.storage.mongodb import Database
from Backened.app.utils.logger import logger


class FeedbackService:
    """Service for managing HR feedback and candidate decisions."""

    def __init__(self) -> None:
        """Initialize FeedbackService with database connection."""
        self.db = Database.get_db()
        logger.info("FeedbackService initialized")

    def update_hr_decision(
        self, 
        candidate_id: Union[str, ObjectId], 
        decision: int
    ) -> bool:
        """
        Record HR feedback/decision on a candidate.
        
        The decision is used to collect labeled training data for model improvement.
        
        Args:
            candidate_id: MongoDB ObjectId or string ID of the candidate
            decision: HR decision (1=Selected, 0=Rejected)
            
        Returns:
            True if feedback was recorded successfully
            
        Raises:
            ValueError: If decision is not 0 or 1
            Exception: If database operation fails
        """
        logger.info(f"Recording feedback for candidate: {candidate_id}")
        
        if decision not in [0, 1]:
            logger.warning(f"Invalid decision value: {decision}")
            raise ValueError("Decision must be 0 (Rejected) or 1 (Selected)")

        try:
            # Convert string to ObjectId if needed
            if isinstance(candidate_id, str):
                candidate_id = ObjectId(candidate_id)

            decision_label = "Selected" if decision == 1 else "Rejected"
            
            result = self.db.candidates.update_one(
                {"_id": candidate_id},
                {
                    "$set": {
                        "ranking.hr_decision": decision
                    }
                }
            )

            if result.matched_count == 0:
                logger.warning(f"Candidate not found: {candidate_id}")
                return False

            logger.info(f"Feedback recorded: {candidate_id} - {decision_label}")
            return True
            
        except Exception as e:
            logger.error(f"Error recording feedback for candidate {candidate_id}: {str(e)}")
            raise