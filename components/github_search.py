import requests

def search_github_repos(paper_title, token):
    query = f'"{paper_title}" in:readme'
    headers = {"Authorization": f"token {token}"}
    url = f"https://api.github.com/search/repositories?q={query}&per_page=3"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()["items"]
    else:
        return []
