from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import time
import logging

from ..schemas.search import SearchRequest, SearchResponse, SearchResult
from .vector_service import VectorService

logger = logging.getLogger(__name__)

class SearchService:
    def __init__(self, db: Session):
        self.db = db
        self.vector_service = VectorService()
    
    def semantic_search(self, request: SearchRequest) -> SearchResponse:
        """Perform semantic search using vector embeddings"""
        start_time = time.time()
        
        try:
            # Perform vector search
            vector_results = self.vector_service.search(
                query=request.query,
                top_k=request.top_k,
                document_ids=request.document_ids,
                score_threshold=request.score_threshold
            )
            
            # Convert to SearchResult objects
            results = [
                SearchResult(
                    id=result["id"],
                    score=result["score"],
                    document_id=result["document_id"],
                    text=result["text"],
                    chunk_index=result["chunk_index"],
                    timestamp=result.get("timestamp"),
                    embedding_model=result.get("embedding_model")
                )
                for result in vector_results
            ]
            
            search_time_ms = (time.time() - start_time) * 1000
            
            return SearchResponse(
                results=results,
                query=request.query,
                total_results=len(results),
                search_time_ms=round(search_time_ms, 2)
            )
            
        except Exception as e:
            logger.error(f"Error in semantic search: {e}")
            raise