import os
import httpx
from app.services.vector_store import search_codebase # Or your search function
from app.services.llm.factory import get_llm # Your LLM abstraction factory

async def generate_and_post_ai_review(repo_name: str, pr_number: int, modified_files: list):
    """
    Gathers context, prompts the local LLM to review the changes, 
    and posts the result as a comment on the GitHub PR.
    """
    print(f"🤖 [AI REVIEWER] Generating review for PR #{pr_number}...")

    # 1. Gather context or summarize modified files for the LLM prompt
    file_names = [f["filename"] for f in modified_files]
    files_context_summary = ", ".join(file_names)

    # 2. Build the engineering prompt for Qwen 2.5 Coder
    prompt = f"""
    You are DevMind AI, an expert Principal Software Engineer conducting an automated code review.
    The following files were modified in Pull Request #{pr_number}: {files_context_summary}.
    
    Please review these modifications for:
    1. Potential security vulnerabilities or injection flaws.
    2. Performance bottlenecks or anti-patterns.
    3. Readability and maintainability issues.

    Provide a concise, constructive, and professional code review with markdown formatting.
    """

    # 3. Call your swappable LLM provider factory
    llm = get_llm() # Uses your Ollama / qwen2.5-coder instance
    review_comment = await llm.generate_answer(prompt)

    # 4. Post the review comment back to GitHub via REST API
    github_token = os.getenv("GITHUB_TOKEN")
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"Bearer {github_token}"
    }
    
    # GitHub Issues and PR comments use the exact same endpoint path!
    url = f"https://api.github.com/repos/{repo_name}/issues/{pr_number}/comments"
    payload = {
        "body": f"### 🧠 DevMind AI Code Review\n\n{review_comment}"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)
        
        if response.status_code == 201:
            print(f"✅ Successfully posted AI review comment to PR #{pr_number}!")
        else:
            print(f"❌ [GITHUB API ERROR] Failed to post comment: {response.text}")