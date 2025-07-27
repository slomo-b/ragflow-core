from fastapi import APIRouter

from .endpoints import documents, search, health

api_router = APIRouter()

# Health check
api_router.include_router(health.router, prefix="/health", tags=["health"])

# Document management
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])

# Search functionality
api_router.include_router(search.router, prefix="/search", tags=["search"])
