from fastapi import FastAPI, HTTPException
import uuid
import traceback
import json

from app.schema.root import AnalyzeRequest
from app.utility.analysis import get_pr_data,get_url_data,gemini_analysis
from app.utility.storage import r,init_task,get_task,update_task
from app.utility.locale import Config


app = FastAPI(
    title="PotPieAssgn",
    description="Welcome to PotPieAssgn",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str):
    return {"item_id": item_id, "q": q}

@app.post("/analyze-pr")
async def analyze_pr(body: AnalyzeRequest):
    try:
        pr_data = get_pr_data(body.repo_url, body.pr_number, body.github_token)

        task_id = str(uuid.uuid4())
        file=0
        
        init_task(task_id)
        # await update_task(task_id, 'progress', f"{file}/{len(pr_data)}")

        files = []
        num_issues = 0
        num_critical_issues = 0

        for pr in pr_data:
            file += 1
            content = get_url_data(pr['raw_url'])

            response = gemini_analysis(content)
            response = json.loads(response.text.replace('`','').replace('json',''))

            files.append({
                "filename": pr['filename'],
                "url": pr['raw_url'],
                "issues": response,
            })

            num_issues += len(response)
            num_critical_issues += len([issue for issue in response if issue['type'] != 'style'])

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

            # await update_task(task_id, 'progress', f"{file}/{len(pr_data)}")
        return result
    
    except HTTPException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/init-db")
async def init_db():
    success = r.set('foo', 'bar')
    msg = r.get('foo')
    return {"message": "DB initialized", "success": msg == 'bar', "value": await get_task('foo')}