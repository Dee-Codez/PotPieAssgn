import requests
import google.generativeai as genai
from celery import Celery
import json

from app.utility.locale import Config
from app.celery import celery_app
from app.utility.storage import init_task, update_task

genai.configure(api_key=Config.GEMINI_KEY)

def get_pr_data(repo_url, pr_number, github_token):
    headers = {
        'Authorization': f'Bearer {github_token}',
    }
    owner, repo = repo_url.split('/')[-2:]
    response = requests.get(f'https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/files', headers=headers)
    return response.json()

def get_url_data(url):
    response = requests.get(url)
    return response.text

def gemini_analysis(content):
    model = genai.GenerativeModel("gemini-1.5-flash")

    prompt = f"""Analyse the following code snippet and infer a list of possible issues and suggestions to improve the code quality.
    {content}
    Make sure to provide a detailed analysis of the code snippet and format the output in a list of objects with this schema : 
    {{
        "type": "style"/"bug"/"error",
        "line": "line_number in integer",
        "description": "brief description of the issue",
        "suggestion": "suggestion to address the issue"
    }}
    """
    response = model.generate_content(prompt)
    return response


@celery_app.task
async def analyze_pr_task(repo_url, pr_number, github_token, task_id):
    try:
        pr_data = get_pr_data(repo_url, pr_number, github_token)
        file = 0
        
        await update_task(task_id, 'progress', f"{file}/{len(pr_data)}")

        files = []
        num_issues = 0
        num_critical_issues = 0

        for pr in pr_data:
            file += 1
            content = get_url_data(pr['raw_url'])

            response = gemini_analysis(content)
            response = json.loads(response.text.replace('`', '').replace('json', ''))

            files.append({
                "filename": pr['filename'],
                "url": pr['raw_url'],
                "issues": response,
            })

            num_issues += len(response)
            num_critical_issues += len([issue for issue in response if issue.get('type') != 'style'])

            await update_task(task_id, 'progress', f"{file}/{len(pr_data)}")

        result = {
            "task_id": task_id,
            "status": "completed",
            "results": {
                "files": files,
                "summary": {
                    "total_files": len(pr_data),
                    "total_issues": num_issues,
                    "critical_issues": num_critical_issues
                }
            }
        }

        await update_task(task_id, 'completed', result)

        return result
        
    except Exception as e:
        await update_task(task_id, 'failed', str(e))
        raise e