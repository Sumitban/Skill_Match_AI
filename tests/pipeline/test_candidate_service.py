import numpy as np
import pytest
from unittest.mock import patch, MagicMock

from Backened.app.pipeline.candidate_service import CandidateService


@patch("Backened.app.pipeline.candidate_service.Database")
@patch("Backened.app.pipeline.candidate_service.extract_text")
@patch("Backened.app.pipeline.candidate_service.extract_links")
@patch("Backened.app.pipeline.candidate_service.extract_sections")
@patch("Backened.app.pipeline.candidate_service.compute_section_confidence")
@patch("Backened.app.pipeline.candidate_service.GitHubClient")
@patch("Backened.app.pipeline.candidate_service.FeatureBuilder")
@patch("Backened.app.pipeline.candidate_service.EmbeddingModel")
def test_process_candidate_success(
    mock_embedding_model,
    mock_feature_builder,
    mock_github_client,
    mock_confidence,
    mock_extract_sections,
    mock_extract_links,
    mock_extract_text,
    mock_database
):

    # -------------------------
    # Mock Database
    # -------------------------
    mock_db = MagicMock()
    mock_database.get_db.return_value = mock_db

    mock_db.jobs.find_one.return_value = {
        "job_id": "job123",
        "raw_text": "Machine learning engineer",
        "embedding": [0.1, 0.2]
    }

    mock_db.candidates.insert_one.return_value.inserted_id = "candidate_id_1"

    # -------------------------
    # Mock Resume Parsing
    # -------------------------
    mock_extract_text.return_value = "Sample resume text"
    mock_extract_links.return_value = {"github": [], "linkedin": []}
    mock_extract_sections.return_value = {
        "skills": "Python ML",
        "education": "B.Tech"
    }
    mock_confidence.return_value = 0.8

    # -------------------------
    # Mock Feature Builder
    # -------------------------
    mock_feature_builder_instance = MagicMock()
    mock_feature_builder.return_value = mock_feature_builder_instance
    mock_feature_builder_instance.build_feature_vector.return_value = np.array(
        [0.9, 0.8, 0.7, 3, 1, 0, 0, 0, 0]
    )

    # -------------------------
    # Run Service
    # -------------------------
    service = CandidateService()
    result = service.process_candidate("job123", "resume.pdf")

    # -------------------------
    # Assertions
    # -------------------------
    assert result["job_id"] == "job123"
    assert result["candidate_id"] == "candidate_id_1"

    mock_db.candidates.insert_one.assert_called_once()
    
@patch("Backened.app.pipeline.candidate_service.Database")
def test_process_candidate_job_not_found(mock_database):

    mock_db = MagicMock()
    mock_database.get_db.return_value = mock_db
    mock_db.jobs.find_one.return_value = None

    service = CandidateService()

    with pytest.raises(ValueError):
        service.process_candidate("invalid_job", "resume.pdf")