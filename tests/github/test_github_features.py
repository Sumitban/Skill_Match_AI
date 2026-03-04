# tests/github/test_github_features.py

import pytest
from Backened.app.github.github_features import (
    compute_repo_count,
    compute_star_count,
    compute_fork_ratio,
    compute_language_distribution,
    select_top_repositories,
)

MOCK_REPOS = [
    {
        "name": "repo1",
        "stargazers_count": 10,
        "fork": False,
        "language": "Python"
    },
    {
        "name": "repo2",
        "stargazers_count": 5,
        "fork": True,
        "language": "Python"
    },
    {
        "name": "repo3",
        "stargazers_count": 20,
        "fork": False,
        "language": "C++"
    },
]


def test_compute_repo_count():
    assert compute_repo_count(MOCK_REPOS) == 3


def test_compute_star_count():
    assert compute_star_count(MOCK_REPOS) == 35


def test_compute_fork_ratio():
    ratio = compute_fork_ratio(MOCK_REPOS)
    assert ratio == 1 / 3


def test_compute_fork_ratio_empty():
    assert compute_fork_ratio([]) == 0.0


def test_compute_language_distribution():
    langs = compute_language_distribution(MOCK_REPOS)
    assert langs["Python"] == 2
    assert langs["C++"] == 1


def test_select_top_repositories():
    top = select_top_repositories(MOCK_REPOS, top_n=2)
    assert len(top) == 2
    assert top[0]["stargazers_count"] >= top[1]["stargazers_count"]