import chromadb
import os
from chromadb.utils import embedding_functions

# 1. Initialize the ChromaDB client globally (but NOT the AI model yet)
chroma_client = chromadb.PersistentClient(path="./chroma_db")

def get_collection():
    """
    Lazy-loads the embedding model and collection.
    This prevents Render from crashing due to high memory usage on server startup.
    """
    # Fetch your Gemini API key from Render's environment variables
    api_key = os.getenv("GEMINI_API_KEY") 
    
    if not api_key:
        raise ValueError("GEMINI_API_KEY is missing from environment variables!")

    # 2. Use Gemini's cloud API for embeddings (Zero local memory footprint!)
    embedding_model = embedding_functions.GoogleGenerativeAiEmbeddingFunction(
        api_key=api_key,
        task_type="RETRIEVAL_DOCUMENT"
    )
    
    # 3. Create or grab our "Collection"
    return chroma_client.get_or_create_collection(
        name="devmind_codebase",
        embedding_function=embedding_model
    )

def add_chunks_to_db(chunks: list, repo_name: str):
    """
    Takes the AST chunks, generates embeddings, and saves them to ChromaDB.
    """
    if not chunks:
        return 0

    ids = []
    documents = []
    metadatas = []

    for i, chunk in enumerate(chunks):
        chunk_id = f"{repo_name}_chunk_{i}"
        ids.append(chunk_id)
        
        documents.append(chunk["text"])
        
        # Metadata updated for AST chunking logic
        metadatas.append({
            "type": chunk.get("type", "code"),
            "start_line": chunk.get("start_line", 0),
            "end_line": chunk.get("end_line", 0),
            "file_path": chunk.get("file_path", chunk.get("filename", "unknown")), 
            "repo_name" : repo_name
        })

    # Call get_collection() exactly when we need it
    collection = get_collection()
    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas
    )
    
    return len(ids)

def search_codebase(query: str, repo_name: str, top_k: int = 3):
    """
    Converts the user's question into a math vector and searches ChromaDB 
    for the most relevant code chunks.
    """
    collection = get_collection()
    
    # ChromaDB automatically uses our Gemini model to turn the query into numbers
    results = collection.query(
        query_texts=[query],
        n_results=top_k,
        where={"repo_name": repo_name}
    )
    
    return results

def delete_chunks_by_file(file_path: str):
    """
    Deletes all vector chunks associated with a specific file path.
    Crucial for Incremental Indexing to prevent duplicate, stale code.
    """
    try:
        collection = get_collection()
        
        # Delete every vector where the file_path matches this exact string
        collection.delete(
            where={"file_path": file_path}
        )
        print(f"🗑️ [INCREMENTAL INDEX] Deleted stale vectors for: {file_path}")
        
    except ValueError:
        # If the collection doesn't exist yet, we just ignore it.
        pass
    except Exception as e:
        print(f"⚠️ [DB ERROR] Could not delete vectors for {file_path}: {e}")