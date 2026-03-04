import requests
from dotenv import load_dotenv
import base64
from typing import Dict, List
import os

from Backened.app.utils.logger import logger

load_dotenv()

GITHUB_API_BASE = "https://api.github.com"


class GitHubClient:

    def __init__(self):

        token = os.getenv("GITHUB_API_KEY")

        self.headers = {
            "Accept": "application/vnd.github+json"
        }

        if token:
            self.headers["Authorization"] = f"Bearer {token}"

        self.timeout = 10

    # -------------------------------------
    # Fetch user profile
    # -------------------------------------

    def fetch_user_profile(self, username: str) -> Dict:

        url = f"{GITHUB_API_BASE}/users/{username}"

        try:

            response = requests.get(
                url,
                headers=self.headers,
                timeout=self.timeout
            )

            if response.status_code == 404:
                return {}

            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as e:

            logger.warning(f"GitHub profile fetch failed for {username}: {e}")

            return {}

    # -------------------------------------
    # Fetch repositories
    # -------------------------------------

    def fetch_repositories(self, username: str) -> List[Dict]:

        repos = []
        page = 1

        while True:

            url = f"{GITHUB_API_BASE}/users/{username}/repos"

            try:

                response = requests.get(
                    url,
                    headers=self.headers,
                    params={"per_page": 100, "page": page},
                    timeout=self.timeout
                )

                if response.status_code == 404:
                    return []

                if response.status_code == 403:
                    logger.warning("GitHub rate limit reached")
                    return repos

                response.raise_for_status()

                batch = response.json()

                if not batch:
                    break

                repos.extend(batch)
                page += 1

            except requests.exceptions.RequestException as e:

                logger.warning(f"GitHub repo fetch failed for {username}: {e}")
                break

        return repos

    # -------------------------------------
    # Fetch README
    # -------------------------------------

    def fetch_readme(self, username: str, repo_name: str) -> str:

        url = f"{GITHUB_API_BASE}/repos/{username}/{repo_name}/readme"

        try:

            response = requests.get(
                url,
                headers=self.headers,
                timeout=self.timeout
            )

            if response.status_code != 200:
                return ""

            data = response.json()

            if "content" not in data:
                return ""

            content = base64.b64decode(
                data["content"]
            ).decode("utf-8", errors="ignore")

            return content

        except requests.exceptions.RequestException as e:

            logger.warning(
                f"GitHub README fetch failed for {username}/{repo_name}: {e}"
            )

            return ""