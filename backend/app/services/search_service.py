# File: backend/app/services/search_service.py
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import time
import logging
import re

from ..schemas.search import SearchRequest, SearchResponse, SearchResult
from ..models.document import Document
from .vector_service import VectorService

logger = logging.getLogger(__name__)

class SearchService:
    def __init__(self, db: Session):
        self.db = db
        self.vector_service = VectorService()
    
    async def semantic_search(self, request: SearchRequest) -> SearchResponse:
        """Perform semantic search using vector embeddings"""
        start_time = time.time()
        
        try:
            logger.info(f"Performing semantic search for: '{request.query}' (top_k={request.top_k})")
            
            # Perform vector search
            vector_results = await self.vector_service.search(
                query=request.query,
                top_k=request.top_k * 2,  # Get more results for filtering
                document_ids=request.document_ids,
                score_threshold=max(request.score_threshold, 0.1)  # Minimum threshold
            )
            
            # Get document information and deduplicate
            results = []
            seen_documents = set()
            
            for result in vector_results:
                doc_id = result["document_id"]
                
                # Skip if we already have this document (deduplicate)
                if doc_id in seen_documents:
                    continue
                
                # Get document info
                document = self.db.query(Document).filter(Document.id == doc_id).first()
                if not document:
                    continue
                
                # Filter out low-quality matches
                if not self._is_relevant_content(result["text"], request.query):
                    continue
                
                seen_documents.add(doc_id)
                
                # Create enhanced result
                enhanced_result = SearchResult(
                    id=result["id"],
                    score=result["score"],
                    document_id=doc_id,
                    text=self._clean_and_highlight_text(result["text"], request.query),
                    chunk_index=result["chunk_index"],
                    timestamp=result.get("timestamp"),
                    embedding_model=result.get("embedding_model"),
                    document_filename=document.filename,  # Add filename
                    document_type=document.content_type   # Add file type
                )
                
                results.append(enhanced_result)
                
                # Stop when we have enough unique results
                if len(results) >= request.top_k:
                    break
            
            # Sort by relevance score
            results.sort(key=lambda x: x.score, reverse=True)
            
            search_time_ms = (time.time() - start_time) * 1000
            
            logger.info(f"Search completed: {len(results)} unique results in {search_time_ms:.2f}ms")
            
            return SearchResponse(
                results=results,
                query=request.query,
                total_results=len(results),
                search_time_ms=round(search_time_ms, 2)
            )
            
        except Exception as e:
            logger.error(f"Error in semantic search: {e}")
            raise
    
    def _is_relevant_content(self, text: str, query: str) -> bool:
        """Check if the text content is relevant to the query"""
        # Skip very short fragments
        if len(text.strip()) < 20:
            return False
        
        # Skip fragments that are mostly URLs
        url_pattern = r'https?://[^\s]+'
        urls = re.findall(url_pattern, text)
        if len(''.join(urls)) > len(text) * 0.7:  # More than 70% URLs
            return False
        
        # Skip fragments that are mostly random characters/IDs
        if len(re.findall(r'[a-f0-9]{32,}', text)) > 2:  # Multiple long hex strings
            return False
        
        # Check for query terms in content (case insensitive)
        query_words = query.lower().split()
        text_lower = text.lower()
        
        # At least one query word should be present for very short queries
        if len(query_words) <= 2:
            return any(word in text_lower for word in query_words if len(word) > 2)
        
        return True
    
    def _clean_and_highlight_text(self, text: str, query: str) -> str:
        """Clean and potentially highlight relevant parts of text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Limit length for better display
        if len(text) > 500:
            # Try to find a good cutoff point near a sentence
            cutoff = text.find('. ', 400)
            if cutoff > 300:
                text = text[:cutoff + 1] + "..."
            else:
                text = text[:500] + "..."
        
        return text
    
    async def hybrid_search(self, request: SearchRequest) -> SearchResponse:
        """Perform hybrid search (semantic + keyword)"""
        # For now, just use semantic search but with better filtering
        return await self.semantic_search(request)
    
    async def keyword_search(self, request: SearchRequest) -> SearchResponse:
        """Perform keyword search in document content"""
        start_time = time.time()
        
        try:
            # Search in document content using database
            query_terms = request.query.lower().split()
            
            # Build SQL query for keyword search
            documents = self.db.query(Document).filter(
                Document.status == "completed",
                Document.content.isnot(None)
            )
            
            # Filter by document IDs if specified
            if request.document_ids:
                documents = documents.filter(Document.id.in_(request.document_ids))
            
            results = []
            for doc in documents.limit(request.top_k * 2):  # Get more for filtering
                content = doc.content.lower() if doc.content else ""
                
                # Check if any query terms are in content
                matches = []
                for term in query_terms:
                    if len(term) > 2 and term in content:
                        matches.append(term)
                
                if matches:
                    # Calculate simple relevance score
                    score = len(matches) / len(query_terms)
                    
                    # Find best excerpt
                    excerpt = self._find_best_excerpt(doc.content, request.query)
                    
                    result = SearchResult(
                        id=f"keyword_{doc.id}",
                        score=score,
                        document_id=str(doc.id),
                        text=excerpt,
                        chunk_index=0,
                        timestamp=doc.created_at.isoformat() if doc.created_at else None,
                        embedding_model="keyword_search",
                        document_filename=doc.filename,
                        document_type=doc.content_type
                    )
                    results.append(result)
            
            # Sort by score and limit
            results.sort(key=lambda x: x.score, reverse=True)
            results = results[:request.top_k]
            
            search_time_ms = (time.time() - start_time) * 1000
            
            return SearchResponse(
                results=results,
                query=request.query,
                total_results=len(results),
                search_time_ms=round(search_time_ms, 2)
            )
            
        except Exception as e:
            logger.error(f"Error in keyword search: {e}")
            raise
    
    def _find_best_excerpt(self, content: str, query: str, excerpt_length: int = 300) -> str:
        """Find the best excerpt from content that matches the query"""
        if not content:
            return ""
        
        query_words = [word.lower() for word in query.split() if len(word) > 2]
        content_lower = content.lower()
        
        best_start = 0
        best_score = 0
        
        # Try different starting positions
        for start in range(0, len(content) - excerpt_length, 50):
            excerpt = content_lower[start:start + excerpt_length]
            
            # Count query word matches in this excerpt
            score = sum(1 for word in query_words if word in excerpt)
            
            if score > best_score:
                best_score = score
                best_start = start
        
        # Extract the best excerpt
        excerpt = content[best_start:best_start + excerpt_length]
        
        # Clean up the excerpt
        if best_start > 0:
            excerpt = "..." + excerpt
        if best_start + excerpt_length < len(content):
            excerpt = excerpt + "..."
        
        return excerpt.strip()
    
    async def get_search_suggestions(self, partial_query: str, limit: int = 5) -> List[str]:
        """Get search suggestions based on document content"""
        try:
            # Get completed documents
            documents = self.db.query(Document).filter(
                Document.status == "completed",
                Document.content.isnot(None)
            ).limit(20)
            
            suggestions = set()
            partial_lower = partial_query.lower()
            
            for doc in documents:
                if doc.content:
                    # Extract words that start with the partial query
                    words = re.findall(r'\b\w+', doc.content.lower())
                    for word in words:
                        if (word.startswith(partial_lower) and 
                            len(word) > len(partial_lower) and 
                            len(word) <= 20):
                            suggestions.add(word)
                
                if len(suggestions) >= limit * 2:
                    break
            
            # Sort by length (shorter first) and return limited results
            return sorted(list(suggestions))[:limit]
            
        except Exception as e:
            logger.error(f"Error getting search suggestions: {e}")
            return []