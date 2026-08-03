from fastapi import APIRouter, HTTPException
from app.schemas.ingest import IngestRequest
from app.services.github import parse_github_url, fetch_repo_tree, is_valid_code_file, download_file_content
from app.services.ast_parser import extract_ast_chunks

# 1. NEW IMPORT: Bring in your vector database service
from app.services.vector_store import add_chunks_to_db 

router = APIRouter()

@router.post("/ingest")
async def ingest_repository(payload: IngestRequest):
    try:
        url_str = str(payload.repo_url)
        owner, repo = parse_github_url(url_str)
        tree = await fetch_repo_tree(owner, repo)
        
        valid_files = [
            item for item in tree 
            if item["type"] == "blob" and is_valid_code_file(item["path"])
        ]
        
        saved_files = []
        total_chunks = 0
        
        # 2. NEW: We need a master list to hold every chunk we find across all files
        all_chunks_to_store = []
        
        for item in valid_files[:10]: 
            content = await download_file_content(owner, repo, "main", item["path"])
            
            if content:
                # FIXED: Pass the actual GitHub file path dynamically
                chunks = extract_ast_chunks(content, file_path=item["path"])
                total_chunks += len(chunks)
                
                # 3. NEW: Add these chunks to our master list
                all_chunks_to_store.extend(chunks)
                
                saved_files.append({
                    "path": item["path"], 
                    "chunks_extracted": len(chunks)
                })
        
        # 4. NEW: Send the master list of chunks to the AI model and Vector Database!
        total_vectors = 0
        if all_chunks_to_store:
            repo_identifier = f"{owner}_{repo}"
            total_vectors = add_chunks_to_db(all_chunks_to_store, repo_identifier)
                
        return {
            "status": "success",
            "repository": f"{owner}/{repo}",
            "total_files_in_repo": len(tree),
            "valid_code_files_found": len(valid_files),
            "total_ast_chunks_extracted": total_chunks,
            "vectors_stored_in_db": total_vectors, # 5. NEW: Show the user how many vectors were saved!
            "preview": saved_files
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")