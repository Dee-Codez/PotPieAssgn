from pydantic import BaseModel
from typing import Optional

class Root(BaseModel):
    message: str = "Welcome to PotPieAssgn"


class AnalyzeRequest(BaseModel):
    repo_url: str
    pr_number: int
    github_token: Optional[str] = None