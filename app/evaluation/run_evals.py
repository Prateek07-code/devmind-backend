import asyncio
# Adjust this import to match wherever your ChromaDB search function lives!
from app.services.vector_store import search_codebase 

# 1. Define our test dataset: (Question -> Expected File Path)
EVAL_DATASET = [
    (
        "Where is the logic that parses abstract syntax trees using tree-sitter?",
        "ast_parser.py"
    ),
    (
        "Explain the step-by-step logic inside the generate_stream method of the OllamaProvider class.",
        "ollama_provider.py"
    ),
    (
        "Which file handles incoming GitHub URLs and filters out junk files?",
        "github.py"
    ),
    (
        "Where is the base LLM provider abstract class defined?",
        "base.py"
    )
]

async def run_evaluation():
    print("🚀 Starting RAG Evaluation Suite...\n")
    hits = 0
    total = len(EVAL_DATASET)

    for i, (question, expected_file) in enumerate(EVAL_DATASET):
        print(f"Test {i+1}/{total}")
        print(f"Q: {question}")
        print(f"Expected: {expected_file}")

        # 2. Retrieve top 3 chunks from ChromaDB
        # (Make sure search_codebase returns a list of dictionaries with metadata)
        try:
            # 2. Retrieve results from ChromaDB
            results = search_codebase(question)
            
            retrieved_files = []
            
            # Check if it returned ChromaDB's native dictionary format
            if isinstance(results, dict) and "metadatas" in results:
                # ChromaDB wraps results in a list of lists, so we grab index [0]
                metadatas = results["metadatas"][0] 
                
                # Extract the file path from each metadata dictionary
                retrieved_files = [
                    meta.get("file_path", "") for meta in metadatas if meta
                ]
            else:
                print("❌ RESULT: ERROR -> Unrecognized database output format.")
                continue
            
            # 3. Check for a hit
            is_hit = any(expected_file in file_path for file_path in retrieved_files)

            if is_hit:
                print("✅ RESULT: HIT\n")
                hits += 1
            else:
                print("❌ RESULT: MISS")
                print(f"Actually retrieved: {retrieved_files}\n")
                
        except Exception as e:
            print(f"❌ RESULT: ERROR -> {str(e)}\n")

    hit_rate = (hits / total) * 100
    print("=" * 40)
    print(f"🏆 FINAL HIT RATE: {hit_rate:.2f}% ({hits}/{total})")
    print("=" * 40)

if __name__ == "__main__":
    asyncio.run(run_evaluation())