import numpy as np
from unittest.mock import MagicMock
from Backened.app.features.feature_builder import FeatureBuilder


def test_feature_vector_length():

    mock_embedding = MagicMock()
    mock_embedding.encode.return_value = np.array([0.5, 0.5])

    builder = FeatureBuilder(mock_embedding)

    resume = {
        "raw_text": "ML engineer",
        "skills_text": "Python ML",
        "skills": ["Python", "ML"],
        "years_experience": 3
    }

    github = {
        "readme_text": "ML project",
        "repo_count": 2,
        "total_stars": 10,
        "fork_ratio": 0.2,
        "language_distribution": {"Python": 2}
    }

    jd_embedding = np.array([0.5, 0.5])
    jd_text = "Looking for Python ML engineer"

    features = builder.build_feature_vector(
        resume, github, jd_embedding, jd_text
    )

    assert len(features) == 9