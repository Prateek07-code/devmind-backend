from pydantic import BaseModel

class QueryRequest(BaseModel):
    # This ensures the user MUST send a field called 'question' containing text.
    question: str