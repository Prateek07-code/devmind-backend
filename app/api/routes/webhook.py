from fastapi import APIRouter, Request, Header, HTTPException,BackgroundTasks
from typing import Dict, Any
from app.services.orchestrator import process_pr_review
import hmac
import hashlib
import os

router = APIRouter()

@router.post("/github")
async def github_webhook_listener(
    request: Request, 
    background_tasks: BackgroundTasks
):
    # Extract GitHub Event Header
    github_event = request.headers.get("X-GitHub-Event")
    
    # Handle initial Ping event from GitHub setup
    if github_event == "ping":
        return {"status": "success", "message": "Pong! Webhook configured properly."}
    
    # We only want to process Pull Request events
    if github_event != "pull_request":
        return {"status": "ignored", "message": f"Event '{github_event}' ignored."}

    payload: Dict[str, Any] = await request.json()
    action = payload.get("action")

    # Target actions: 'opened' (new PR) or 'synchronize' (code updated in existing PR)
    if action not in ["opened", "synchronize"]:
        return {"status": "ignored", "message": f"PR Action '{action}' ignored."}

    # Extract Key PR Metadata
    pr_number = payload["pull_request"]["number"]
    repo_name = payload["repository"]["full_name"]
    commit_sha = payload["pull_request"]["head"]["sha"]
    pr_title = payload["pull_request"]["title"]

    print(f"\n⚡ [WORKFLOW TRIGGERED] Pull Request #{pr_number} ({action}) in {repo_name}")
    print(f"📌 PR Title: {pr_title}")
    print(f"🔑 Target Commit SHA: {commit_sha}\n")

    # Delegate heavy processing (diff calculation, AST re-indexing, LLM review) to background task
    background_tasks.add_task(process_pr_review, repo_name, pr_number, commit_sha)

    return {
        "status": "processing", 
        "pr_number": pr_number,
        "action": action
    }