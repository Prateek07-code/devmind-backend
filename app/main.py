from fastapi import FastAPI
import app.config  
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import query  # adjust import path if needed
from app.api.routes.webhook import router as webhook_router

from app.api.routes.ingest import router as ingest_router
# 1. NEW: Import the query router
from app.api.routes.query import router as query_router 

app = FastAPI(title="DevMind AI Engine")

# Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # React Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingest_router, prefix="/api", tags=["Repository Ingestion"])
# 2. NEW: Plug the query router into the app
app.include_router(query.router, prefix="/query", tags=["query"]) 
app.include_router(webhook_router,prefix="/api/webhook", tags=["Webhooks"])

@app.get("/")
def read_root():
    return {"status": "online", "message": "DevMind API is running"}