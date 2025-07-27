from fastapi import APIRouter

from .endpoints import health, documents, search, collections

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    health.router,
    prefix="/health",
    tags=["Health"]
)

api_router.include_router(
    documents.router,
    prefix="/documents",
    tags=["Documents"]
)

api_router.include_router(
    search.router,
    prefix="/search",
    tags=["Search"]
)

api_router.include_router(
    collections.router,
    prefix="/collections",
    tags=["Collections"]
)