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
            "file_path": chunk.get("file_path", chunk.get("filename", "unknown"))  # Added this line
        })

    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas
    )
    
    return len(ids)

def search_codebase(query: str, n_results: int = 3):
    """
    Converts the user's question into a math vector and searches ChromaDB 
    for the most relevant code chunks.
    """
    # ChromaDB automatically uses our all-MiniLM-L6-v2 model to turn the query into numbers!
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )
    
    return results