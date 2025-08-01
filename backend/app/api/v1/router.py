# File: backend/app/api/v1/router.py
from fastapi import APIRouter

from .endpoints import health, documents, search, chat, collections

api_router = APIRouter()

# Health endpoints
api_router.include_router(
    health.router,
    prefix="/health",
    tags=["health"]
)

# Document management
api_router.include_router(
    documents.router,
    prefix="/documents",
    tags=["documents"]
)

# Search functionality
api_router.include_router(
    search.router,
    prefix="/search",
    tags=["search"]
)

# Chat & RAG functionality
api_router.include_router(
    chat.router,
    prefix="/chat",
    tags=["chat", "rag"]
)

# Collections management
api_router.include_router(
    collections.router,
    prefix="/collections",
    tags=["collections"]
)