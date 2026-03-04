# tests/ingestion/test_section_detector.py

import pytest
from Backened.app.ingestion.section_detector import extract_sections

def test_basic_sections_extraction():
    text = """
    SKILLS
    Python, ML, NLP

    EXPERIENCE
    Worked at Company X for 2 years

    EDUCATION
    B.Tech in Computer Science
    """

    sections = extract_sections(text)

    assert "skills" in sections
    assert "experience" in sections
    assert "education" in sections
    assert "Python" in sections["skills"]


def test_mixed_case_headers():
    text = """
    Skills
    Python

    Work Experience
    Did something

    Education
    B.Tech
    """

    sections = extract_sections(text)

    assert "skills" in sections
    assert "experience" in sections
    assert "education" in sections


def test_no_headers_fallback():
    text = "This resume has no clear sections. Just plain text."

    sections = extract_sections(text)

    assert "full_text" in sections
    assert sections["full_text"] == text.strip()


def test_duplicate_headers_merge():
    text = """
    SKILLS
    Python

    SKILLS
    ML
    """

    sections = extract_sections(text)

    assert "skills" in sections
    assert "Python" in sections["skills"]
    assert "ML" in sections["skills"]