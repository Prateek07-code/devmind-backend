import os
import sys

# 1. Go up TWO levels to reach 'devmind-backend' (the root folder)
# This allows Python to recognize the 'app' module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.services.ast_parser import extract_ast_chunks
from app.services.vector_store import add_chunks_to_db

def ingest_local_directory(directory_path: str):
    print(f"📂 Scanning directory: {directory_path}")
    all_chunks = []
    
    for root, _, files in os.walk(directory_path):
        # Skip virtual environments and hidden folders
        if "venv" in root or ".git" in root or "__pycache__" in root:
            continue
            
        for file_name in files:
            if file_name.endswith(".py"):
                full_path = os.path.join(root, file_name)
                
                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    
                # Extract chunks using your shiny new updated parser!
                chunks = extract_ast_chunks(content, file_path=full_path)
                all_chunks.extend(chunks)
                
    if all_chunks:
        print(f"🚀 Found {len(all_chunks)} total chunks. Saving to ChromaDB...")
        total_vectors = add_chunks_to_db(all_chunks, repo_name="devmind_local")
        print(f"✅ Successfully saved {total_vectors} vectors!")
    else:
        print("❌ No python files or chunks found.")

if __name__ == "__main__":
    # 2. Since this script is inside app/evaluation, going up one level gives us the main 'app' folder to scan
    APP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
    ingest_local_directory(APP_DIR)