from fastapi import APIRouter, HTTPException
from app.schemas.query import QueryRequest
from app.services.vector_store import search_codebase
from app.services.llm.factory import get_llm 
from typing import Dict, Any

router = APIRouter()

def build_augmented_prompt(question: str, retrieved_chunks: list) -> str:
    """
    Takes the retrieved code chunks and formats them into a single string
    so the LLM can read them as context.
    """
    context_text = ""
    for i, chunk in enumerate(retrieved_chunks):
        context_text += f"\n--- Code Snippet {i+1} ---\n{chunk}\n"
        
    prompt = f"""
    You are an expert senior software engineer. 
    Please answer the user's question based ONLY on the provided code snippets. 
    If the code snippets do not contain the answer, politely state that you cannot answer based on the current context.

    User Question: {question}

    Relevant Code Context:
    {context_text}
    """
    return prompt

@router.post("/query")
async def ask_question(payload: QueryRequest):
    try:
        # 1. RETRIEVAL
        search_results = search_codebase(query=payload.question, n_results=3)
        documents = search_results.get("documents")

        if not documents:
            return {
                "status": "success",
                "answer": "No relevant documents found."
            }

        retrieved_chunks = documents[0]
        
        if not retrieved_chunks:
             return {"status": "success", "answer": "No relevant code found in the database."}

        # 2. AUGMENTATION
        augmented_prompt = build_augmented_prompt(payload.question, retrieved_chunks)
        
        # 3. GENERATION
        llm_provider = get_llm()
        system_prompt = "You are DevMind AI, an intelligent coding assistant."
        
        # Pass the augmented prompt to Ollama
        ai_response = await llm_provider.generate_answer(
            prompt=augmented_prompt, 
            system_prompt=system_prompt
        )
        
        return {
            "status": "success",
            "question": payload.question,
            "chunks_used": len(retrieved_chunks),
            "answer": ai_response
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")