# tests/ingestion/test_section_confidence.py
import pytest
from Backened.app.ingestion.section_confidence import compute_section_confidence, is_confident


def test_high_confidence():
    sections = {
        "skills": "Python ML NLP TensorFlow PyTorch SQL",
        "experience": "Worked at X for 5 years building ML systems.",
        "education": "B.Tech in Computer Science"
    }

    score = compute_section_confidence(sections)

    assert score >= 0.66
    assert is_confident(score)


def test_low_confidence():
    sections = {
        "skills": "Python",
    }

    score = compute_section_confidence(sections)

    assert score < 0.6
    assert not is_confident(score)


def test_confidence_boundary():
    sections = {
        "skills": "Python ML NLP TensorFlow PyTorch SQL",
        "experience": "Worked at X for 2 years building systems."
    }

    score = compute_section_confidence(sections)

    assert 0 <= score <= 1