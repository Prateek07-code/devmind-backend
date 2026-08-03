from pydantic import BaseModel, HttpUrl

class IngestRequest(BaseModel):
    # This ensures the user MUST send a field called 'repo_url', and it MUST be a valid web link.
    repo_url: HttpUrl