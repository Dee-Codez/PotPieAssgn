import requests

def get_pr_data(repo_url, pr_number, github_token):
    headers = {
        'Authorization': f'Bearer {github_token}',
    }
    owner, repo = repo_url.split('/')[-2:]
    response = requests.get(f'https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/files', headers=headers)
    print(owner, repo, pr_number)
    return response.json()

def get_url_data(url):
    response = requests.get(url)
    print(url)
    print(response.text)
    return response.text