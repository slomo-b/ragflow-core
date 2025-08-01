# File: backend/app/services/rag_service.py
from typing import List, Dict, Any, Optional
import logging
from sqlalchemy.orm import Session

from .llm_service import LLMService, LLMProvider
from .vector_service import VectorService
from .search_service import SearchService
from ..schemas.chat import ChatRequest, ChatResponse, SearchResult

logger = logging.getLogger(__name__)

class RAGService:
    """Retrieval Augmented Generation service"""
    
    def __init__(self, db: Session):
        self.db = db
        self.llm_service = LLMService()
        self.vector_service = VectorService()
        self.search_service = SearchService(db)
        
        # RAG Configuration
        self.max_context_chunks = 5
        self.max_context_length = 4000
        self.chunk_overlap_threshold = 0.8
    
    async def chat_with_documents(
        self, 
        request: ChatRequest,
        collection_id: Optional[str] = None
    ) -> ChatResponse:
        """Main RAG endpoint - chat with documents"""
        
        try:
            logger.info(f"Processing chat request: {request.message[:100]}...")
            
            # 1. Retrieve relevant context
            context_chunks = await self._retrieve_context(
                query=request.message,
                collection_id=collection_id,
                top_k=request.max_results or self.max_context_chunks
            )
            
            logger.info(f"Retrieved {len(context_chunks)} context chunks")
            
            # 2. Build conversation messages
            messages = self._build_conversation_messages(
                query=request.message,
                context_chunks=context_chunks,
                conversation_history=request.conversation_history or []
            )
            
            # 3. Generate response
            llm_result = await self.llm_service.generate_response(
                messages=messages,
                provider=LLMProvider(request.provider) if request.provider else None,
                max_tokens=request.max_tokens or 1000,
                temperature=request.temperature or 0.7
            )
            
            # 4. Format response
            response = ChatResponse(
                message=llm_result["response"],
                sources=context_chunks,
                provider=llm_result["provider"],
                tokens_used=llm_result["tokens"],
                success=llm_result["success"],
                metadata={
                    "chunks_retrieved": len(context_chunks),
                    "context_length": sum(len(chunk.text) for chunk in context_chunks),
                    "search_query": request.message
                }
            )
            
            if not llm_result["success"]:
                response.error = llm_result.get("error")
            
            logger.info(f"Chat response generated successfully: {len(response.message)} chars")
            return response
            
        except Exception as e:
            logger.error(f"Error in RAG chat: {e}")
            return ChatResponse(
                message="I apologize, but I encountered an error while processing your request. Please try again.",
                sources=[],
                provider="error",
                tokens_used=0,
                success=False,
                error=str(e)
            )
    
    async def _retrieve_context(
        self, 
        query: str, 
        collection_id: Optional[str] = None,
        top_k: int = 5
    ) -> List[SearchResult]:
        """Retrieve relevant document chunks for context"""
        
        try:
            # Use semantic search to find relevant chunks
            search_results = await self.search_service.semantic_search(
                query=query,
                collection_id=collection_id,
                limit=top_k * 2  # Get more results for filtering
            )
            
            # Filter and rank results
            filtered_chunks = self._filter_and_rank_chunks(
                chunks=search_results,
                query=query,
                max_chunks=top_k
            )
            
            return filtered_chunks
            
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return []
    
    def _filter_and_rank_chunks(
        self, 
        chunks: List[SearchResult], 
        query: str,
        max_chunks: int
    ) -> List[SearchResult]:
        """Filter and rank chunks for optimal context"""
        
        if not chunks:
            return []
        
        # Remove duplicates based on similarity threshold
        unique_chunks = []
        for chunk in chunks:
            is_duplicate = False
            for existing in unique_chunks:
                # Simple text similarity check
                if self._calculate_text_similarity(chunk.text, existing.text) > self.chunk_overlap_threshold:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_chunks.append(chunk)
        
        # Sort by relevance score (already sorted from vector search)
        sorted_chunks = sorted(unique_chunks, key=lambda x: x.score, reverse=True)
        
        # Limit by max chunks and context length
        selected_chunks = []
        total_length = 0
        
        for chunk in sorted_chunks:
            if len(selected_chunks) >= max_chunks:
                break
            if total_length + len(chunk.text) > self.max_context_length:
                break
            
            selected_chunks.append(chunk)
            total_length += len(chunk.text)
        
        logger.info(f"Filtered to {len(selected_chunks)} chunks (total length: {total_length})")
        return selected_chunks
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Simple text similarity calculation"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _build_conversation_messages(
        self, 
        query: str,
        context_chunks: List[SearchResult],
        conversation_history: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        """Build conversation messages for LLM"""
        
        messages = []
        
        # System prompt with context
        system_prompt = self._build_system_prompt(context_chunks)
        messages.append({
            "role": "system",
            "content": system_prompt
        })
        
        # Add conversation history (keep last 10 messages)
        recent_history = conversation_history[-10:] if conversation_history else []
        for msg in recent_history:
            messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })
        
        # Add current user query
        messages.append({
            "role": "user",
            "content": query
        })
        
        return messages
    
    def _build_system_prompt(self, context_chunks: List[SearchResult]) -> str:
        """Build system prompt with retrieved context"""
        
        if not context_chunks:
            return """You are a helpful AI assistant. Answer the user's questions to the best of your ability. 
            If you don't know something, please say so honestly."""
        
        context_text = "\n\n".join([
            f"Document: {chunk.document_filename}\nContent: {chunk.text}"
            for chunk in context_chunks
        ])
        
        return f"""You are a helpful AI assistant that answers questions based on the provided document context.

INSTRUCTIONS:
1. Use the provided context to answer the user's question accurately
2. If the answer is not in the provided context, say so honestly
3. When possible, mention which document(s) your answer comes from
4. Be concise but thorough in your responses
5. If you quote directly from the documents, use quotation marks

CONTEXT FROM DOCUMENTS:
{context_text}

Remember: Base your answers primarily on the provided context. If the context doesn't contain relevant information, let the user know."""

    async def simple_chat(
        self, 
        message: str,
        provider: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> ChatResponse:
        """Simple chat without document context (for testing)"""
        
        try:
            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful AI assistant. Answer questions clearly and concisely."
                },
                {
                    "role": "user", 
                    "content": message
                }
            ]
            
            llm_result = await self.llm_service.generate_response(
                messages=messages,
                provider=LLMProvider(provider) if provider else None,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return ChatResponse(
                message=llm_result["response"],
                sources=[],
                provider=llm_result["provider"],
                tokens_used=llm_result["tokens"],
                success=llm_result["success"],
                metadata={"mode": "simple_chat"}
            )
            
        except Exception as e:
            logger.error(f"Error in simple chat: {e}")
            return ChatResponse(
                message="I apologize, but I encountered an error. Please try again.",
                sources=[],
                provider="error",
                tokens_used=0,
                success=False,
                error=str(e)
            )
    
    def get_available_providers(self) -> List[str]:
        """Get available LLM providers"""
        return self.llm_service.get_available_providers()
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of RAG service components"""
        
        health = {
            "rag_service": "healthy",
            "providers": {},
            "vector_service": "unknown",
            "search_service": "unknown"
        }
        
        # Check LLM providers
        for provider_name in self.llm_service.get_available_providers():
            try:
                provider = LLMProvider(provider_name)
                is_healthy = await self.llm_service.check_provider_health(provider)
                health["providers"][provider_name] = "healthy" if is_healthy else "unhealthy"
            except Exception as e:
                health["providers"][provider_name] = f"error: {str(e)}"
        
        # Check vector service (simple check)
        try:
            # Try to connect to vector service
            collections = self.vector_service.client.get_collections()
            health["vector_service"] = "healthy"
        except Exception as e:
            health["vector_service"] = f"error: {str(e)}"
        
        health["search_service"] = "healthy"  # Assume healthy if no errors
        
        return health