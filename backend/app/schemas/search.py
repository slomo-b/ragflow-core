# File: backend/app/schemas/search.py
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000, description="Search query text")
    top_k: int = Field(5, ge=1, le=50, description="Number of results to return")
    document_ids: Optional[List[str]] = Field(None, description="Filter by specific document IDs")
    score_threshold: float = Field(0.0, ge=0.0, le=1.0, description="Minimum similarity score")
    search_type: str = Field("semantic", description="Search type: semantic, keyword, or hybrid")
    
    @validator('query')
    def query_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Query cannot be empty')
        return v.strip()
    
    @validator('document_ids')
    def validate_document_ids(cls, v):
        if v is not None:
            # Remove empty strings and duplicates
            v = list(set([doc_id.strip() for doc_id in v if doc_id.strip()]))
            if len(v) == 0:
                return None
        return v
    
    @validator('search_type')
    def validate_search_type(cls, v):
        allowed_types = {"semantic", "keyword", "hybrid"}
        if v not in allowed_types:
            raise ValueError(f'Search type must be one of: {", ".join(allowed_types)}')
        return v

class SearchResult(BaseModel):
    id: str = Field(..., description="Unique result ID")
    score: float = Field(..., description="Similarity score (0.0-1.0)")
    document_id: str = Field(..., description="Source document ID")
    text: str = Field(..., description="Matching text chunk")
    chunk_index: int = Field(..., description="Index of chunk within document")
    timestamp: Optional[str] = Field(None, description="When the chunk was indexed")
    embedding_model: Optional[str] = Field(None, description="Model used for embeddings")
    document_filename: Optional[str] = Field(None, description="Original filename")
    document_type: Optional[str] = Field(None, description="Document content type")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "score": 0.85,
                "document_id": "doc_123",
                "text": "This is a sample text chunk that matches the search query.",
                "chunk_index": 2,
                "timestamp": "2025-07-29T01:00:00",
                "embedding_model": "all-MiniLM-L6-v2",
                "document_filename": "example.pdf",
                "document_type": "application/pdf"
            }
        }

class SearchResponse(BaseModel):
    results: List[SearchResult] = Field(..., description="Search results")
    query: str = Field(..., description="Original search query")
    total_results: int = Field(..., description="Total number of results found")
    search_time_ms: float = Field(..., description="Search execution time in milliseconds")
    search_type: str = Field("semantic", description="Type of search performed")
    
    class Config:
        json_schema_extra = {
            "example": {
                "results": [
                    {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "score": 0.85,
                        "document_id": "doc_123",
                        "text": "This is a sample text chunk.",
                        "chunk_index": 2,
                        "timestamp": "2025-07-29T01:00:00",
                        "embedding_model": "all-MiniLM-L6-v2",
                        "document_filename": "example.pdf",
                        "document_type": "application/pdf"
                    }
                ],
                "query": "sample search",
                "total_results": 1,
                "search_time_ms": 45.2,
                "search_type": "semantic"
            }
        }

class SearchSuggestionsResponse(BaseModel):
    suggestions: List[str] = Field(..., description="Search suggestions")
    
    class Config:
        json_schema_extra = {
            "example": {
                "suggestions": [
                    "machine learning",
                    "machine learning algorithms",
                    "machine learning models"
                ]
            }
        }