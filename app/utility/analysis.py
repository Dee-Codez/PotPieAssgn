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
