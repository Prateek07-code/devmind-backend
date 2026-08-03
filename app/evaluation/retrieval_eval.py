import sys
import os

# Ensure the root directory is in python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.services.vector_store import search_codebase

print("🚀 Starting evaluation script...", flush=True)

# 1. Define the Ground Truth Dataset
EVAL_DATASET = [
    {
        "query": "How does the project parse code files into vectors?",
        "expected_file": "vector_store.py"
    },
    {
        "query": "Where is the FastAPI router for querying the AI defined?",
        "expected_file": "query.py"
    },
    {
        "query": "How is the Ollama provider implemented?",
        "expected_file": "ollama_provider.py"
    }
]

def evaluate_retrieval(k=3):
    print(f"--- Running Retrieval Evaluation (Top-{k}) ---", flush=True)
    
    hits = 0
    mrr_sum = 0.0
    
    for item in EVAL_DATASET:
        query = item["query"]
        expected_file = item["expected_file"]
        
        print(f"\nQuery: '{query}'", flush=True)
        
        # 1. Search ChromaDB
        results = search_codebase(query=query, n_results=k)
        
        # 2. Extract metadata array from ChromaDB's dict response
        retrieved_metadatas = results.get("metadatas", [[]])[0] if results else []
        
        # 3. Print debug info
        print("  DEBUG Top Results Metadata:", flush=True)
        for i, meta in enumerate(retrieved_metadatas):
            print(f"   [{i+1}] {meta}", flush=True)
        
        # 4. Check for Hits / Calculate Rank
        hit_found = False
        for rank, metadata in enumerate(retrieved_metadatas):
            if not metadata:
                continue
            
            # Extract file_path safely
            file_path = metadata.get("file_path", "") or ""
            
            if expected_file in file_path:
                hits += 1
                mrr_sum += (1.0 / (rank + 1))
                hit_found = True
                print(f"✅ Hit at rank {rank + 1}!", flush=True)
                break
                
        if not hit_found:
            print(f"❌ Miss. Expected '{expected_file}' but didn't find it in top {k}.", flush=True)

    # 5. Calculate final metrics
    total_queries = len(EVAL_DATASET)
    hit_rate = hits / total_queries if total_queries > 0 else 0
    mrr = mrr_sum / total_queries if total_queries > 0 else 0
    
    print("\n--- Final Results ---", flush=True)
    print(f"Total Queries: {total_queries}", flush=True)
    print(f"Hit Rate: {hit_rate * 100:.2f}%", flush=True)
    print(f"MRR:       {mrr:.4f}", flush=True)

if __name__ == "__main__":
    evaluate_retrieval(k=3)