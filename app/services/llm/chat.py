from app.services.vector_store import search_codebase
# Import whatever function you use to call your LLM (HuggingFace, OpenAI, etc.)
from app.services.llm.base import call_llm 

def ask_codebase(user_query: str) -> str:
    """
    The main RAG pipeline: Retrieves relevant code chunks and passes them 
    to the LLM to generate an answer.
    """
    print(f"🔍 Searching codebase for: '{user_query}'...")
    
    # 1. Retrieve the top 5 chunks
    results = search_codebase(query=user_query, n_results=5)
    
    # Extract the actual code text from the ChromaDB results
    retrieved_documents = results.get("documents", [[]])[0] if results else []
    
    if not retrieved_documents:
        return "I couldn't find any relevant code in the repository to answer that."

    # 2. Format the context into a single string
    formatted_context = "\n\n---\n\n".join(retrieved_documents)
    
    # 3. Build the Prompt Template
    prompt = f"""You are a senior developer answering questions about a codebase.
Use the following retrieved code snippets to answer the user's question. 
If the answer is not contained in the snippets, say "I don't have enough context to answer that." Do not guess.

RETRIEVED CONTEXT:
{formatted_context}

USER QUESTION: 
{user_query}

ANSWER:"""

    print("🧠 Generating answer with LLM...")
    
    # 4. Send it to the LLM
    response = call_llm(prompt)
    
    return response

# Quick local test!
if __name__ == "__main__":
    test_q = "How does the project parse code files into vectors?"
    print(ask_codebase(test_q))