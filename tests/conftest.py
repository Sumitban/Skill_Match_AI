"""
Pytest configuration and fixtures for Skill Match AI tests.
Provides mocks, fixtures, and test utilities for the test suite.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Test constants
TEST_JOB_ID = "test_job_001"
TEST_CANDIDATE_ID = "507f1f77bcf86cd799439011"
TEST_RESUME_PATH = "tests/data/sample_resume.pdf"
TEST_GITHUB_USERNAME = "testuser"


# ===========================================================
# Database Fixtures
# ===========================================================

@pytest.fixture
def mock_database():
    """Mock MongoDB database for testing."""
    mock_db = MagicMock()
    mock_db.jobs = MagicMock()
    mock_db.candidates = MagicMock()
    return mock_db


@pytest.fixture
def mock_mongo_client(mock_database):
    """Mock MongoDB client."""
    with patch('Backened.app.storage.mongodb.MongoClient') as mock_client:
        mock_instance = MagicMock()
        mock_instance.__getitem__.return_value = mock_database
        mock_instance.admin.command.return_value = {"ok": 1}
        mock_client.return_value = mock_instance
        yield mock_client


# ===========================================================
# Service Fixtures
# ===========================================================

@pytest.fixture
def mock_embedding_model():
    """Mock embedding model."""
    mock_model = MagicMock()
    # Return a normalized embedding vector
    mock_model.encode.return_value = [0.5] * 384  # Typical embedding size
    return mock_model


@pytest.fixture
def mock_github_client():
    """Mock GitHub client."""
    mock_client = MagicMock()
    mock_client.fetch_user_profile.return_value = {
        "login": TEST_GITHUB_USERNAME,
        "public_repos": 5,
        "followers": 10
    }
    mock_client.fetch_repositories.return_value = [
        {
            "name": "test_repo_1",
            "stargazers_count": 10,
            "fork": False,
            "language": "Python"
        },
        {
            "name": "test_repo_2",
            "stargazers_count": 5,
            "fork": True,
            "language": "JavaScript"
        }
    ]
    mock_client.fetch_readme.return_value = "# Test Repository\nThis is a test."
    return mock_client


# ===========================================================
# Request Data Fixtures
# ===========================================================

@pytest.fixture
def job_create_request():
    """Sample job creation request."""
    return {
        "job_id": TEST_JOB_ID,
        "title": "Senior Python Developer",
        "raw_text": """
        We are looking for a senior Python developer with 5+ years of experience.
        Required skills: Python, FastAPI, MongoDB, Machine Learning.
        Nice to have: Docker, Kubernetes, AWS.
        """
    }


@pytest.fixture
def candidate_create_request():
    """Sample candidate creation request."""
    return {
        "job_id": TEST_JOB_ID,
        "resume_path": TEST_RESUME_PATH
    }


@pytest.fixture
def feedback_request():
    """Sample feedback request."""
    return {
        "candidate_id": TEST_CANDIDATE_ID,
        "decision": 1  # Selected
    }


# ===========================================================
# Document Fixtures
# ===========================================================

@pytest.fixture
def sample_job_document():
    """Sample job document from database."""
    return {
        "_id": "507f1f77bcf86cd799439001",
        "job_id": TEST_JOB_ID,
        "title": "Senior Python Developer",
        "raw_text": "Senior Python Developer required...",
        "embedding": [0.5] * 384,
        "metadata": {
            "created_at": datetime.utcnow(),
            "updated_at": None
        }
    }


@pytest.fixture
def sample_candidate_document():
    """Sample candidate document from database."""
    return {
        "_id": TEST_CANDIDATE_ID,
        "job_id": TEST_JOB_ID,
        "resume": {
            "raw_text": "John Doe\nPython Developer...",
            "skills": ["Python", "FastAPI", "MongoDB"],
            "years_experience": 5,
            "links": {
                "github": ["testuser"],
                "linkedin": ["john-doe"],
                "email": ["john@example.com"],
                "phoneno": ["+1234567890"]
            }
        },
        "github": {
            "username": TEST_GITHUB_USERNAME,
            "repo_count": 5,
            "total_stars": 15,
            "fork_ratio": 0.2,
            "language_distribution": {"Python": 2, "JavaScript": 1},
            "readme_text": "# Test Project"
        },
        "similarity": {
            "resume_jd": 0.85,
            "skills_jd": 0.9,
            "github_jd": 0.7
        },
        "features": [0.85, 0.9, 0.7, 5, 3, 5, 15, 0.2, 2],
        "ranking": {
            "prediction_score": 0.82,
            "hr_decision": None,
            "rank_position": None
        },
        "metadata": {
            "created_at": datetime.utcnow(),
            "updated_at": None,
            "confidence_score": 0.85
        }
    }


@pytest.fixture
def feature_vector():
    """Sample feature vector for candidate."""
    import numpy as np
    return np.array([0.85, 0.9, 0.7, 5, 3, 5, 15, 0.2, 2], dtype=float)


# ===========================================================
# Configuration Fixtures
# ===========================================================

@pytest.fixture
def test_config():
    """Test configuration."""
    from Backened.app.config import TestingConfig
    return TestingConfig()


# ===========================================================
# HTTP Client Fixtures
# ===========================================================

@pytest.fixture
def mock_requests():
    """Mock requests library."""
    with patch('requests.get') as mock_get, \
         patch('requests.post') as mock_post:
        yield {"get": mock_get, "post": mock_post}


# ===========================================================
# Pytest Hooks and Configuration
# ===========================================================

def pytest_configure(config):
    """Configure pytest before test collection."""
    # Register custom markers
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )


# ===========================================================
# Cleanup Fixtures
# ===========================================================

@pytest.fixture(autouse=True)
def reset_mocks():
    """Reset all mocks after each test."""
    yield
    # Cleanup code here if needed


@pytest.fixture(scope="session")
def test_data_dir():
    """Get the test data directory."""
    return Path(__file__).parent / "data"


# ===========================================================
# Parametrize Fixtures
# ===========================================================

def pytest_generate_tests(metafunc):
    """Generate tests with parameters."""
    if "decision" in metafunc.fixturenames:
        metafunc.parametrize("decision", [0, 1])


# ===========================================================
# Logger Fixture
# ===========================================================

@pytest.fixture
def mock_logger():
    """Mock logger for testing."""
    with patch('Backened.app.utils.logger.logger') as mock:
        yield mock
