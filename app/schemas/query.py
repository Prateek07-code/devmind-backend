from pydantic import BaseModel
from typing import Optional
class QueryRequest(BaseModel):
    # This ensures the user MUST send a field called 'question' containing text.
    question: str
    repo_url: Optional[str] = None