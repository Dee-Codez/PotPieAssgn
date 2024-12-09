import redis
import json 
import psycopg2

from app.utility.locale import Config

r = redis.Redis(
    host=Config.REDIS_HOST,
    port=Config.REDIS_PORT,
    decode_responses=True,
    username=Config.REDIS_USERNAME,
    password=Config.REDIS_PASSWORD,
)

def get_postgres_connection():
    return psycopg2.connect(Config.POSTGRES_URL)

def init_task(task_id):
   
    r.hset(f"task:{task_id}", mapping={
        "task_id": task_id,
        "status": "initiated",
        "progress": "0",
    })

def get_task(task_id):
    task_json = r.hgetall(f"task:{task_id}")
    if task_json == {}:
        return None
    return task_json

def update_task(task_id, key, value):
    if key not in ['', " ", None]:
        r.hset(f"task:{task_id}", key, value)
    else:
        task = value
        r.hset(f"task:{task_id}", mapping={
            "task_id": task_id,
            "status": task['status'],
            "progress": task['progress'],
        })

def store_results(task_id, result):
    conn = get_postgres_connection()
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO results (task_id, result) VALUES (%s, %s)",
            (task_id, json.dumps(result))
        )
    conn.commit()

    
def execute_query(query, params):
    conn = get_postgres_connection()
    with conn.cursor() as cur:
        cur.execute(query, params)
        conn.commit()

def get_results(task_id):
    conn = get_postgres_connection()
    
    task_query = "SELECT * FROM tasks WHERE task_id = %s"
    file_query = "SELECT * FROM files WHERE task_id = %s"
    
    with conn.cursor() as cur:
        cur.execute(task_query, (task_id,))
        task = cur.fetchall()
        
        cur.execute(file_query, (task_id,))
        files = cur.fetchall()
    
    if not task:
        return None
    
    list = []
    for file in files:
        list.append({
            "file": file[0],
            "filename": file[2],
            "url": file[3],
            "issues": file[4]
        })


    result = {
        "task_id": task[0][0],
        "status": task[0][1],
        "results": {
            "files": list,
            "summary": {
                "total_files": task[0][2],
                "total_issues": task[0][3],
                "critical_issues": task[0][4]
            }
        }
    }
    
    return result
    