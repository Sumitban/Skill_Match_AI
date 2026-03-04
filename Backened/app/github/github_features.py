

from typing import List, Dict


def compute_repo_count(repos: List[Dict]) -> int:
    return len(repos)


def compute_star_count(repos: List[Dict]) -> int:
    return sum(repo.get("stargazers_count", 0) for repo in repos)


def compute_fork_ratio(repos: List[Dict]) -> float:
    if not repos:
        return 0.0

    forked = sum(1 for repo in repos if repo.get("fork"))
    return forked / len(repos)


def compute_language_distribution(repos: List[Dict]) -> Dict[str, int]:
    language_count = {}

    for repo in repos:
        lang = repo.get("language")
        if lang:
            language_count[lang] = language_count.get(lang, 0) + 1

    return language_count


def select_top_repositories(repos: List[Dict], top_n: int = 3) -> List[Dict]:
    return sorted(
        repos,
        key=lambda r: r.get("stargazers_count", 0),
        reverse=True
    )[:top_n]
    
def aggregate_readme_text(client, username, repos):
    combined_text = ""

    top_repos = select_top_repositories(repos)

    for repo in top_repos:
        readme = client.fetch_readme(username, repo["name"])
        combined_text += "\n" + readme

    return combined_text.strip()