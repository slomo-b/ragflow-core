# File: backend/app/schemas/chat.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime

class SearchResult(BaseModel):
    """Search result for document chunks"""
    id: str
    document_id: str
    document_filename: str
    text: str
    score: float
    chunk_index: int
    metadata: Optional[Dict[str, Any]] = None

class ConversationMessage(BaseModel):
    """Single message in conversation history"""
    role: str = Field(..., description="Message role: user, assistant, or system")
    content: str = Field(..., description="Message content")
    timestamp: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

class ChatRequest(BaseModel):
    """Request for chat with documents"""
    message: str = Field(..., description="User message/question")
    collection_id: Optional[str] = Field(None, description="Optional collection to search in")
    conversation_history: Optional[List[ConversationMessage]] = Field(None, description="Previous conversation messages")
    
    # LLM parameters
    provider: Optional[str] = Field(None, description="LLM provider: gemini, ollama")
    max_tokens: Optional[int] = Field(1000, description="Maximum tokens to generate")
    temperature: Optional[float] = Field(0.7, description="Generation temperature (0.0-1.0)")
    
    # Search parameters
    max_results: Optional[int] = Field(5, description="Maximum context chunks to retrieve")
    
    class Config:
        schema_extra = {
            "example": {
                "message": "What are the main points discussed in the documents?",
                "collection_id": "default",
                "provider": "gemini",
                "max_tokens": 500,
                "temperature": 0.7,
                "max_results": 5
            }
        }

class ChatResponse(BaseModel):
    """Response from chat with documents"""
    message: str = Field(..., description="Generated response")
    sources: List[SearchResult] = Field(default=[], description="Source chunks used for context")
    
    # Generation metadata
    provider: str = Field(..., description="LLM provider used")
    tokens_used: int = Field(0, description="Estimated tokens used")
    success: bool = Field(True, description="Whether generation was successful")
    error: Optional[str] = Field(None, description="Error message if failed")
    
    # Additional metadata
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional response metadata")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        schema_extra = {
            "example": {
                "message": "Based on the documents, the main points include...",
                "sources": [
                    {
                        "id": "chunk_123",
                        "document_id": "doc_456",
                        "document_filename": "report.pdf",
                        "text": "The key findings show...",
                        "score": 0.85,
                        "chunk_index": 2
                    }
                ],
                "provider": "gemini",
                "tokens_used": 245,
                "success": True,
                "metadata": {
                    "chunks_retrieved": 3,
                    "context_length": 1500
                }
            }
        }

class SimpleChatRequest(BaseModel):
    """Simple chat request without documents"""
    message: str = Field(..., description="User message")
    provider: Optional[str] = Field(None, description="LLM provider")
    max_tokens: Optional[int] = Field(1000, description="Maximum tokens")
    temperature: Optional[float] = Field(0.7, description="Temperature")
    
    class Config:
        schema_extra = {
            "example": {
                "message": "Hello, how are you?",
                "provider": "gemini",
                "max_tokens": 100,
                "temperature": 0.7
            }
        }

class ProvidersResponse(BaseModel):
    """Available LLM providers"""
    providers: List[str] = Field(..., description="List of available providers")
    default_provider: Optional[str] = Field(None, description="Default provider")
    
    class Config:
        schema_extra = {
            "example": {
                "providers": ["gemini", "ollama"],
                "default_provider": "gemini"
            }
        }

class HealthCheckResponse(BaseModel):
    """Health check for RAG service"""
    rag_service: str
    providers: Dict[str, str]
    vector_service: str
    search_service: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        schema_extra = {
            "example": {
                "rag_service": "healthy",
                "providers": {
                    "gemini": "healthy",
                    "ollama": "healthy"
                },
                "vector_service": "healthy", 
                "search_service": "healthy"
            }
        }