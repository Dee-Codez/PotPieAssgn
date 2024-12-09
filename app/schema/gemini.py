import enum

from pydantic import BaseModel, Field

class ISSUE_TYPE(str, enum.Enum):
    STYLE = "style"
    BUG = "bug"
    ERROR = "error"

class Issue(BaseModel):
    type: ISSUE_TYPE
    line: int = Field(..., description="line_number in integer")
    description: str = Field(..., description="brief description of the issue")
    suggestion: str = Field(..., description="suggestion to address the issue")