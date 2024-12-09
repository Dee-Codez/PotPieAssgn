from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import RedirectResponse
import uuid
import traceback
import json

from app.schema.root import AnalyzeRequest
from app.utility.storage import r,init_task,get_task,update_task, get_results
from app.utility.locale import Config
from app.tasks import analyze_pr_task


app = FastAPI(
    title="PotPieAssgn",
    description="Welcome to PotPieAssgn",
    version="1.0.0"
)

@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")

@app.post("/analyze-pr")
async def analyze_pr(body: AnalyzeRequest, background_tasks: BackgroundTasks):
    try:
        
        task_id = str(uuid.uuid4())
        init_task(task_id)

        # analyze_pr_task.delay(body.repo_url, body.pr_number, body.github_token, task_id)
        background_tasks.add_task(analyze_pr_task, body.repo_url, body.pr_number, body.github_token, task_id)
        
        return {"task_id": task_id}
    
    except HTTPException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    

@app.get("/status/{task_id}")
async def get_task_status(task_id: str):
    try:

        return get_task(task_id)
    
    except HTTPException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/result/{task_id}")
async def get_task_result(task_id: str):
    try:
        task = get_task(task_id)
        if task is None:
            raise HTTPException(status_code=400, detail="Task not found")
        elif task.get('status') == 'failed':
            raise HTTPException(status_code=400, detail="Task failed. Check status for error details")
        elif task.get('status') == 'completed':
            return get_results(task_id)
        else:
            raise HTTPException(status_code=400, detail="Task is not completed yet")
    except HTTPException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
