import chromadb
from chromadb.utils import embedding_functions

# 1. Initialize the ChromaDB client 
# PersistentClient saves the data to a hidden folder on your hard drive so you don't lose it when the server stops.
chroma_client = chromadb.PersistentClient(path="./chroma_data")

# 2. Load a fast, free, local embedding model
# 'all-MiniLM-L6-v2' is an industry-standard model that converts text into a 384-dimensional vector.
embedding_model = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

# 3. Create or grab our "Collection" (Think of a collection like a table in a standard SQL database)
collection = chroma_client.get_or_create_collection(
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
        
        # --- METADATA UPDATED HERE ---
        metadatas.append({
            "type": chunk.get("type", "code"),
            "start_line": chunk.get("start_line", 0),
            "end_line": chunk.get("end_line", 0),
            "file_path": chunk.get("file_path", chunk.get("filename", "unknown")),  # Added this line
            "repo_name" : repo_name
        })

    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas
    )
    
    return len(ids)

def search_codebase(query: str,repo_name:str, top_k: int = 3):
    """
    Converts the user's question into a math vector and searches ChromaDB 
    for the most relevant code chunks.
    """
    # ChromaDB automatically uses our all-MiniLM-L6-v2 model to turn the query into numbers!
    results = collection.query(
        query_texts=[query],
        n_results=top_k,
        where ={"repo_name":repo_name}
    )
    
    return results

def delete_chunks_by_file(file_path: str):
    """
    Deletes all vector chunks associated with a specific file path.
    This is crucial for Incremental Indexing to prevent duplicate, stale code in the DB.
    """
    try:
        # Connect to our existing collection
        collection = chroma_client.get_collection(name="devmind_codebase")
        
        # ChromaDB allows us to delete based on the metadata we saved earlier!
        # We tell it: "Delete every vector where the file_path matches this exact string."
        collection.delete(
            where={"file_path": file_path}
        )
        print(f"🗑️ [INCREMENTAL INDEX] Deleted stale vectors for: {file_path}")
        
    except ValueError:
        # If the collection doesn't exist yet, we just ignore it.
        pass
    except Exception as e:
        print(f"⚠️ [DB ERROR] Could not delete vectors for {file_path}: {e}")