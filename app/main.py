from fastapi import FastAPI

from app.schema.root import AnalyzeRequest
from app.utility.analysis import get_pr_data,get_url_data

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
def analyze_pr(body: AnalyzeRequest):
    pr_data = get_pr_data(body.repo_url, body.pr_number, body.github_token)
    response = {}
    for pr in pr_data:
        response[pr['filename']] = get_url_data(pr['raw_url'])

    return response

