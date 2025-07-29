# File: backend/app/api/v1/endpoints/search.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from ....core.database import get_db
from ....services.search_service import SearchService
from ....schemas.search import SearchRequest, SearchResponse

router = APIRouter()

@router.post("/semantic", response_model=SearchResponse)
async def semantic_search(
    request: SearchRequest,
    db: Session = Depends(get_db)
):
    """
    Perform semantic search using vector embeddings
    
    - **query**: The search query text
    - **top_k**: Number of results to return (1-50)
    - **document_ids**: Optional list of document IDs to search within
    - **score_threshold**: Minimum similarity score (0.0-1.0)
    """
    service = SearchService(db)
    return await service.semantic_search(request)

@router.get("/", response_model=SearchResponse)
async def quick_search(
    q: str = Query(..., description="Search query"),
    top_k: int = Query(5, ge=1, le=50, description="Number of results"),
    document_ids: Optional[str] = Query(None, description="Comma-separated document IDs"),
    score_threshold: float = Query(0.0, ge=0.0, le=1.0, description="Minimum similarity score"),
    db: Session = Depends(get_db)
):
    """
    Quick search endpoint with query parameters
    
    - **q**: Search query text
    - **top_k**: Number of results to return
    - **document_ids**: Optional comma-separated document IDs
    - **score_threshold**: Minimum similarity score
    """
    service = SearchService(db)
    
    # Parse document IDs if provided
    doc_ids_list = None
    if document_ids:
        doc_ids_list = [doc_id.strip() for doc_id in document_ids.split(",") if doc_id.strip()]
    
    # Create request object
    request = SearchRequest(
        query=q,
        top_k=top_k,
        document_ids=doc_ids_list,
        score_threshold=score_threshold
    )
    
    return await service.semantic_search(request)

@router.post("/hybrid", response_model=SearchResponse)
async def hybrid_search(
    request: SearchRequest,
    db: Session = Depends(get_db)
):
    """
    Perform hybrid search (semantic + keyword matching)
    
    - **query**: The search query text
    - **top_k**: Number of results to return (1-50)
    - **document_ids**: Optional list of document IDs to search within
    - **score_threshold**: Minimum similarity score (0.0-1.0)
    """
    service = SearchService(db)
    return await service.hybrid_search(request)

@router.get("/suggestions")
async def get_search_suggestions(
    q: str = Query(..., description="Partial search query"),
    limit: int = Query(5, ge=1, le=20, description="Number of suggestions"),
    db: Session = Depends(get_db)
):
    """
    Get search suggestions based on partial query
    
    - **q**: Partial search query
    - **limit**: Number of suggestions to return
    """
    service = SearchService(db)
    suggestions = await service.get_search_suggestions(q, limit)
    return {"suggestions": suggestions}