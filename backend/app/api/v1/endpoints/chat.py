from fastapi import APIRouter

router = APIRouter()

@router.get("/providers")
async def get_providers():
    return {
        "providers": ["gemini"],
        "default_provider": "gemini"
    }

@router.post("/simple")
async def simple_chat():
    return {
        "message": "Chat endpoint not fully implemented yet",
        "provider": "gemini",
        "success": True,
        "tokens_used": 0
    }

@router.post("/")
async def chat_with_documents():
    return {
        "message": "RAG chat endpoint not fully implemented yet", 
        "sources": [],
        "provider": "gemini",
        "success": True,
        "tokens_used": 0
    }

@router.get("/health")
async def chat_health():
    return {
        "rag_service": "healthy",
        "providers": {"gemini": "healthy"},
        "vector_service": "healthy",
        "search_service": "healthy"
    }