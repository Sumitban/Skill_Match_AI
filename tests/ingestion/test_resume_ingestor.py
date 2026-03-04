import pytest

# tests/ingestion/test_resume_ingestor.py

from Backened.app.ingestion.resume_ingestor import extract_links


def test_extract_links_basic():
    text = """
    Contact me at test@example.com
    GitHub: https://github.com/sumit123
    LinkedIn: https://linkedin.com/in/sumit-profile
    """

    links = extract_links(text)

    assert "sumit123" in links["github"]
    assert "test@example.com" in links["email"]
    assert "sumit-profile" in links["linkedin"]


def test_extract_links_no_links():
    text = "This text has no contact information."

    links = extract_links(text)

    assert links["github"] == []
    assert links["linkedin"] == []
    assert links["email"] == []