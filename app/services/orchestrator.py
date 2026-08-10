import httpx
from typing import List
from app.services.github import get_pr_modified_files
from app.services.vector_store import delete_chunks_by_file, add_chunks_to_db
from app.services.ast_parser import extract_ast_chunks# Adjust imports based on your Week 2 setup
from app.services.reviewer import generate_and_post_ai_review

async def process_pr_review(repo_name: str, pr_number: int, commit_sha: str):
    print(f"\n🚀 [BACKGROUND TASK] Starting Incremental Indexing for PR #{pr_number}")

    # 1. Fetch the exact files that changed
    modified_files = await get_pr_modified_files(repo_name, pr_number)

    if not modified_files:
        print("🤷‍♂️ No valid code files modified. Aborting incremental indexing.")
        return

    new_chunks_to_store = []

    # 2. Process each file one by one
    async with httpx.AsyncClient() as client:
        for file_data in modified_files:
            filename = file_data["filename"]
            status = file_data["status"]
            raw_url = file_data["raw_url"]

            print(f"🔄 Processing {filename} (Status: {status})")

            # STEP 2 (The Wipe): Always delete the old vectors for this file to prevent duplicates
            delete_chunks_by_file(filename)

            # STEP 3 (The Re-Index): If the file was added or modified, parse the new code
            if status in ["added", "modified"] and raw_url:
                response = await client.get(raw_url)
                if response.status_code == 200:
                    code_text = response.text
                    
                    # Run it through the Week 2 Surgeon's Scalpel (Tree-sitter)
                    # Note: You may need to adapt these 2 lines slightly based on your exact Week 2 AST parser names
                    parser = get_language_parser(filename) 
                    tree = parser.parse(bytes(code_text, "utf8"))
                    
                    # Extract the intact functions and classes
                    chunks = walk_tree(tree.root_node, bytes(code_text, "utf8"), filename)
                    new_chunks_to_store.extend(chunks)

    # 4. Save the updated vectors in one efficient batch
    if new_chunks_to_store:
        print(f"💾 Saving {len(new_chunks_to_store)} updated chunks to ChromaDB...")
        add_chunks_to_db(new_chunks_to_store)

    # 5. Trigger Agent 2 to review the code and comment on GitHub
    await generate_and_post_ai_review(repo_name, pr_number, modified_files)

    print(f"✅ [BACKGROUND TASK] Incremental Indexing complete for PR #{pr_number}")
    # (Step 4: Triggering the AI PR Reviewer will go right here next!)