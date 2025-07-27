from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class SearchRequest(BaseModel):
    query: str = Field(..., description="Search query text")
    top_k: int = Field(5, ge=1, le=50, description="Number of results to return")
    document_ids: Optional[List[str]] = Field(None, description="Filter by specific document IDs")
    score_threshold: float = Field(0.0, ge=0.0, le=1.0, description="Minimum similarity score")

class SearchResult(BaseModel):
    id: str
    score: float
    document_id: str
    text: str
    chunk_index: int
    timestamp: Optional[str] = None
    embedding_model: Optional[str] = None

class SearchResponse(BaseModel):
    results: List[SearchResult]
    query: str
    total_results: int
    search_time_ms: float