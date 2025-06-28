import requests

def search_github_repos(paper_title: str, token: str, per_page: int = 3):
    """
    Broadly searches GitHub repositories for the given paper title,
    looking in name, description, README—or even code files.
    Returns the top `per_page` results.
    """
    # Prepare a more flexible qualifier:
    #  • Drop exact quotes so partial matches count
    #  • Search in name, description, README, and code
    qualifier = f'{paper_title} in:name,description,readme,code'

    url = "https://api.github.com/search/repositories"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "MyResearchApp/1.0"
    }
    params = {
        "q": qualifier,
        "per_page": per_page,
        "sort": "stars",
        "order": "desc",
    }

    resp = requests.get(url, headers=headers, params=params)
    if resp.status_code == 200:
        return resp.json().get("items", [])
    else:
        print(f"GitHub API error {resp.status_code}: {resp.text}")
        return []
