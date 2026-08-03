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

    # Prepare the data in the exact format ChromaDB requires
    for i, chunk in enumerate(chunks):
        # We need a unique ID for every single chunk
        chunk_id = f"{repo_name}_chunk_{i}"
        ids.append(chunk_id)
        
        # The actual code text
        documents.append(chunk["text"])
        
        # Metadata helps us filter later (e.g., "Only search in Python files")
        metadatas.append({
            "type": chunk["type"],
            "start_line": chunk["start_line"],
            "end_line": chunk["end_line"]
        })

    # Insert everything into the database in one massive batch!
    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas
    )
    
    return len(ids)