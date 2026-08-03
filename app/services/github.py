import httpx
import re
from app.config import GITHUB_TOKEN

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