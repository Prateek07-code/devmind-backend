from fastapi import FastAPI
import app.config  

from app.api.routes.ingest import router as ingest_router
# 1. NEW: Import the query router
from app.api.routes.query import router as query_router 

app = FastAPI(title="DevMind AI Engine")

app.include_router(ingest_router, prefix="/api", tags=["Repository Ingestion"])
# 2. NEW: Plug the query router into the app
app.include_router(query_router, prefix="/api", tags=["Code QA"]) 

@app.get("/")
def read_root():
    return {"status": "online", "message": "DevMind API is running"}