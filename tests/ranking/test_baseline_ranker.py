# tests/ranking/test_baseline_ranker.py

import numpy as np
import pytest
from unittest.mock import MagicMock, patch
from Backened.app.ranking.baseline_ranker import BaselineRanker


# -----------------------------------
# Test normalize_years
# -----------------------------------

def test_normalize_years_basic():
    ranker = BaselineRanker()
    assert ranker.normalize_years(5) == 0.5


def test_normalize_years_cap():
    ranker = BaselineRanker()
    # capped at max_years=10
    assert ranker.normalize_years(20) == 1.0


# -----------------------------------
# Test compute_score
# -----------------------------------

def test_compute_score_weighting():
    ranker = BaselineRanker()

    # feature vector format:
    # [resume_sim, skills_sim, github_sim, years_exp, ...]
    feature_vector = np.array([1.0, 0.5, 0.0, 10.0, 0, 0, 0, 0, 0])

    score = ranker.compute_score(feature_vector)

    # normalized_years = 1.0
    expected = (
        0.4 * 1.0 +
        0.3 * 0.5 +
        0.2 * 0.0 +
        0.1 * 1.0
    )

    assert pytest.approx(score, 0.0001) == expected


# -----------------------------------
# Test sorting logic (mock DB)
# -----------------------------------

@patch("Backened.app.ranking.baseline_ranker.Database")
def test_rank_candidates_sorting(mock_db_class):

    # Mock DB instance
    mock_db = MagicMock()
    mock_db_class.get_db.return_value = mock_db

    # Create fake candidates
    candidate1 = {
        "_id": "c1",
        "features": [0.9, 0.8, 0.7, 5, 0, 0, 0, 0, 0]
    }

    candidate2 = {
        "_id": "c2",
        "features": [0.2, 0.1, 0.1, 1, 0, 0, 0, 0, 0]
    }

    mock_db.candidates.find.return_value = [candidate1, candidate2]

    ranker = BaselineRanker()
    results = ranker.rank_candidates("job123")

    # Candidate1 should rank higher
    assert results[0]["candidate_id"] == "c1"
    assert results[1]["candidate_id"] == "c2"


@patch("Backened.app.ranking.baseline_ranker.Database")
def test_rank_position_assignment(mock_db_class):

    mock_db = MagicMock()
    mock_db_class.get_db.return_value = mock_db

    candidate1 = {
        "_id": "c1",
        "features": [0.9, 0.8, 0.7, 5, 0, 0, 0, 0, 0]
    }

    candidate2 = {
        "_id": "c2",
        "features": [0.8, 0.7, 0.6, 4, 0, 0, 0, 0, 0]
    }

    mock_db.candidates.find.return_value = [candidate1, candidate2]

    ranker = BaselineRanker()
    ranker.rank_candidates("job123")

    # Ensure update_one was called twice
    assert mock_db.candidates.update_one.call_count == 2