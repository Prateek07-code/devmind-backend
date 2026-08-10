import httpx
import os
import re
from app.config import GITHUB_TOKEN
from typing import List, Dict, Any

def parse_github_url(url: str):
    """
    Takes a standard GitHub URL and extracts the owner and repository name.
    Example: https://github.com/tiangolo/fastapi -> ('tiangolo', 'fastapi')
    """
    # This is a Regular Expression (Regex) that looks for the exact pattern of a GitHub URL
    pattern = r"github\.com/([^/]+)/([^/]+)"
    match = re.search(pattern, url)
    
    if not match:
        raise ValueError("Invalid GitHub URL format. Please provide a valid public repository URL.")
        
    owner = match.group(1)
    repo = match.group(2)
    
    # Clean up the repo name just in case the user pasted a URL ending in .git
    repo = repo[:-4] if repo.endswith(".git") else repo
    
    return owner, repo

async def fetch_repo_tree(owner: str, repo: str, branch: str = "main"):
    """
    Uses the GitHub REST API to fetch a list of every single file in the repository.
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
    
    # We attach your secret VIP badge (the token) to the request headers
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}
    
    # We open an asynchronous web client to talk to GitHub
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        
        # If GitHub says "404 Not Found", it might be because the default branch is 'master', not 'main'
        if response.status_code == 404 and branch == "main":
            print(f">>> Branch 'main' not found for {owner}/{repo}. Trying 'master'...")
            return await fetch_repo_tree(owner, repo, branch="master")
            
        # If any other error happens (like 403 Rate Limit), this line forces Python to throw an error so we know
        response.raise_for_status()
        
        # We extract the JSON data and return just the "tree" (the list of files)
        return response.json().get("tree", [])


# day4 , junk removal and fetching code
# A "Set" of allowed extensions. (Sets are much faster(O(1),uses hashing to search insead of linear search) for lookups than lists!)
ALLOWED_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".java", 
    ".cpp", ".c", ".go", ".rs", ".md"
}

def is_valid_code_file(file_path: str) -> bool:
    """
    Checks if a file path is a valid source code file we want to analyze.
    Filters out binaries, hidden folders, lock files, and dependencies.
    """
    # 1. The Blacklist: Reject bad directories and known junk files
    ignored_paths = ["node_modules/", "venv/", ".git/", "dist/", "build/", "__pycache__/", "package-lock.json", "yarn.lock"]
    
    if any(ignored in file_path for ignored in ignored_paths):
        return False
        
    # 2. The Whitelist: Only accept files ending in our approved extensions
    return any(file_path.endswith(ext) for ext in ALLOWED_EXTENSIONS)

async def download_file_content(owner: str, repo: str, branch: str, path: str) -> str:
    """
    Downloads the raw text content of a single code file directly from GitHub.
    """
    # Notice we use 'raw.githubusercontent.com' instead of 'api.github.com'
    # This bypasses the GitHub UI and just hands us the pure text of the file.
    raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(raw_url)
        
        # 200 is the standard HTTP status code for "OK / Success"
        if response.status_code == 200:
            return response.text
            
        # If the file fails to download, just return an empty string so the app doesn't crash
        return ""

async def get_pr_modified_files(repo_full_name: str, pr_number: int) -> List[Dict[str, Any]]:
    """
    Calls the GitHub API to fetch the specific files changed in a Pull Request.
    repo_full_name: format 'owner/repo' (e.g., 'pallets/flask')
    """
    github_token = os.getenv("GITHUB_TOKEN")
    
    # GitHub requires these specific headers for API authentication
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"Bearer {github_token}"
    }
    
    # The specific GitHub REST API endpoint for PR files
    url = f"https://api.github.com/repos/{repo_full_name}/pulls/{pr_number}/files"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        
        if response.status_code != 200:
            print(f"❌ [GITHUB API ERROR] Failed to fetch PR #{pr_number} files: {response.text}")
            return []
            
        files_data = response.json()
        modified_files = []
        
        for file in files_data:
            filename = file.get("filename")
            status = file.get("status") # Can be 'added', 'modified', or 'removed'
            raw_url = file.get("raw_url")
            
            # We only want to process files if they match our valid code extensions
            # (Assuming you defined ALLOWED_EXTENSIONS earlier in this file)
            if any(filename.endswith(ext) for ext in ALLOWED_EXTENSIONS):
                modified_files.append({
                    "filename": filename,
                    "status": status,
                    "raw_url": raw_url
                })
                
        print(f"✅ Found {len(modified_files)} valid code files modified in PR #{pr_number}")
        return modified_files

