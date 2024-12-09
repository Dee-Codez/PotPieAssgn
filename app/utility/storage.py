import redis
import json 

from app.utility.locale import Config

r = redis.Redis(
    host=Config.REDIS_HOST,
    port=Config.REDIS_PORT,
    decode_responses=True,
    username=Config.REDIS_USERNAME,
    password=Config.REDIS_PASSWORD,
)

def init_task(task_id):
   
    task = {
        "task_id": task_id,
        "status": "initiated",
        "results": {
            "files": [],
            "summary": {
                "total_files": 0,
                "total_issues": 0,
                "critical_issues": 0
            }
        }
    }

    r.set(task_id, json.dumps(task))

async def get_task(task_id):
    task = r.get(task_id)
    return task

async def update_task(task_id, key, value):
    if key not in ['', " ", None]:
        task = await get_task(task_id)
        task = json.loads(task)
        task[key] = value
    else:
        task = value
    r.set(task_id, json.dumps(task))