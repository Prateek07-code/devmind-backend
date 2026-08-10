from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.schemas.query import QueryRequest
from app.services.vector_store import search_codebase
from app.services.llm.factory import get_llm 
from app.services.github import parse_github_url
import json
import asyncio
import traceback

router = APIRouter()

# Simple global state to remember the currently active repository for chat
_active_repo_identifier = None

def set_active_repo(repo_identifier: str):
    global _active_repo_identifier
    _active_repo_identifier = repo_identifier

def get_active_repo() -> str:
    return _active_repo_identifier


def build_augmented_prompt(question: str, retrieved_chunks: list) -> str:
    """
    Formats retrieved code chunks into context for the LLM.
    """
    context_text = ""
    for i, chunk in enumerate(retrieved_chunks):
        context_text += f"\n--- Code Snippet {i+1} ---\n{chunk}\n"
        
    prompt = f"""
    You are an expert senior software engineer. 
    You are answering a question about a specific codebase.
    
    CRITICAL RULE: You must base your answer STRICTLY on the provided Code Context. 
    Do NOT invent, hallucinate, or assume features exist if they are not in the code.

    User Question: {question}

    Relevant Code Context:
    {context_text}
    """
    return prompt


def resolve_repo_identifier(payload: QueryRequest) -> str:
    """
    Resolves which repository to search: uses payload.repo_url if provided,
    otherwise falls back to the last ingested active repository.
    """
    global _active_repo_identifier
    if payload.repo_url:
        owner, repo = parse_github_url(payload.repo_url)
        repo_identifier = f"{owner}_{repo}"
        set_active_repo(repo_identifier)
        return repo_identifier
    
    if _active_repo_identifier:
        return _active_repo_identifier
        
    raise HTTPException(
        status_code=400, 
        detail="No repository has been ingested yet. Please ingest a repository first."
    )


# ------------------------------------------------------------------
# 1. Standard Batch JSON Endpoint
# ------------------------------------------------------------------
@router.post("/query")
async def ask_question(payload: QueryRequest):
    try:
        repo_identifier = resolve_repo_identifier(payload)

        search_results = search_codebase(query=payload.question, repo_name=repo_identifier, top_k=3)
        documents = search_results.get("documents", [])

        if not documents or not documents[0]:
            return {
                "status": "success",
                "answer": "No relevant code found in the database."
            }

        retrieved_chunks = documents[0]
        augmented_prompt = build_augmented_prompt(payload.question, retrieved_chunks)
        
        llm_provider = get_llm()
        system_prompt = "You are DevMind AI, an intelligent coding assistant."
        
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
        print("🚨 ERROR IN QUERY ROUTE 🚨")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


# ------------------------------------------------------------------
# 2. Real-Time Streaming Endpoint (SSE)
# ------------------------------------------------------------------
@router.post("/stream")
async def ask_question_stream(payload: QueryRequest):
    try:
        repo_identifier = resolve_repo_identifier(payload)

        search_results = search_codebase(query=payload.question, repo_name=repo_identifier, top_k=3)
        documents = search_results.get("documents", [])

        if not documents or not documents[0]:
            async def empty_generator():
                yield f"data: {json.dumps({'text': 'No relevant code found in the database.'})}\n\n"
                yield "data: [DONE]\n\n"
            return StreamingResponse(empty_generator(), media_type="text/event-stream")

        retrieved_chunks = documents[0]
        augmented_prompt = build_augmented_prompt(payload.question, retrieved_chunks)
        
        llm_provider = get_llm()
        system_prompt = "You are DevMind AI, an intelligent coding assistant."

        async def sse_generator():
            if hasattr(llm_provider, "generate_answer_stream"):
                async for chunk in llm_provider.generate_answer_stream(
                    prompt=augmented_prompt, 
                    system_prompt=system_prompt
                ):
                    yield f"data: {json.dumps({'text': chunk})}\n\n"
            else:
                full_response = await llm_provider.generate_answer(
                    prompt=augmented_prompt,
                    system_prompt=system_prompt
                )
                yield f"data: {json.dumps({'text': full_response})}\n\n"

            yield "data: [DONE]\n\n"

        return StreamingResponse(sse_generator(), media_type="text/event-stream")

    except Exception as e:
        print("\n" + "="*50)
        print("🚨 CRITICAL ERROR IN RAG PIPELINE 🚨")
        traceback.print_exc()
        print("="*50 + "\n")
        
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")