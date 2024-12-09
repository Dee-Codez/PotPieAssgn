import json
from celery import Celery

from app.celery import celery_app
from app.utility.analysis import get_pr_data, get_url_data, gemini_analysis
from app.utility.storage import init_task, update_task, store_results, execute_query

@celery_app.task(name="app.utility.analysis.analyze_pr_task")
def analyze_pr_task(repo_url, pr_number, github_token, task_id):
    try:
        pr_data = get_pr_data(repo_url, pr_number, github_token)
        file = 0
        
        init_task(task_id)
        update_task(task_id, 'status', 'processing')
        update_task(task_id, 'progress', f"{file}/{len(pr_data)}")

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

            update_task(task_id, 'progress', f"{file}/{len(pr_data)}")

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
        execute_query(
            "INSERT INTO tasks (task_id, status, total_files, total_issues, critical_issues) VALUES (%s, %s, %s, %s, %s)",
            (task_id, "completed", len(pr_data), num_issues, num_critical_issues)
        )

        for file in files:
            execute_query(
                "INSERT INTO files (task_id, filename, url, issues) VALUES (%s, %s, %s, %s)",
                (task_id, file['filename'], file['url'], json.dumps(file['issues']))
            )
        
        update_task(task_id, 'status', 'completed')
        return result
    except Exception as e:
        update_task(task_id, 'status', 'failed')
        update_task(task_id, 'error', str(e))
        raise e