
import pytest
from unittest.mock import patch
from Backened.app.github.github_client import GitHubClient


@patch("Backened.app.github.github_client.requests.get")
def test_fetch_user_profile_success(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"login": "sumit"}

    client = GitHubClient()
    data = client.fetch_user_profile("sumit")

    assert data["login"] == "sumit"


@patch("Backened.app.github.github_client.requests.get")
def test_fetch_user_profile_not_found(mock_get):
    mock_get.return_value.status_code = 404

    client = GitHubClient()
    data = client.fetch_user_profile("unknown")

    assert data == {}


@patch("Backened.app.github.github_client.requests.get")
def test_fetch_repositories_empty(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = []

    client = GitHubClient()
    repos = client.fetch_repositories("sumit")

    assert repos == []