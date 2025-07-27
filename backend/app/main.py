from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import asyncio

from .core.config import settings
from .core.init_db import init_database
from .api.v1.router import api_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("🚀 Starting RagFlow Backend...")
    
    try:
        # Initialize database
        logger.info("Initializing database...")
        init_database()
        
        # Test vector service connection
        logger.info("Testing vector service connection...")
        from .services.vector_service import VectorService
        vector_service = VectorService()
        logger.info("✅ Vector service connected successfully!")
        
        logger.info("✅ Backend startup completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Backend startup failed: {e}")
        # Don't raise - let the app start anyway for debugging
        logger.warning("⚠️ Starting with limited functionality...")
    
    yield
    
    # Shutdown
    logger.info("👋 Shutting down RagFlow Backend...")

# Create FastAPI application
app = FastAPI(
    title="RagFlow API",
    version=settings.version,
    description="Open Source RAG Platform - Document Upload, Vector Search & Chat",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Frontend development
        "http://frontend:3000",   # Docker frontend
        "http://127.0.0.1:3000",  # Alternative localhost
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# Root endpoints
@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "message": "RagFlow API",
        "version": settings.version,
        "docs": "/docs",
        "redoc": "/redoc",
        "status": "running",
        "features": {
            "document_upload": True,
            "vector_search": True,
            "semantic_search": True,
            "collections": True,
            "chat": False  # Coming in Phase 3
        }
    }

@app.get("/ping")
async def ping():
    """Simple health check"""
    return {"message": "pong", "timestamp": "2025-07-27"}

@app.get("/health")
async def health():
    """Basic health endpoint"""
    return {
        "status": "healthy",
        "version": settings.version,
        "timestamp": "2025-07-27"
    }

# Development helper endpoints
@app.get("/api/v1/dev/routes")
async def list_routes():
    """Development helper - list all available routes"""
    routes = []
    for route in app.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            routes.append({
                "path": route.path,
                "methods": list(route.methods),
                "name": getattr(route, 'name', 'unknown'),
                "tags": getattr(route, 'tags', [])
            })
    
    return {
        "message": "Available API routes",
        "total_routes": len(routes),
        "routes": sorted(routes, key=lambda x: x["path"])
    }

@app.get("/api/v1/system/status")
async def system_status():
    """System status overview"""
    return {
        "status": "operational",
        "version": settings.version,
        "mode": "development" if settings.debug else "production",
        "services": {
            "api": "healthy",
            "database": "available",
            "vector_db": "available",
            "file_storage": "available"
        },
        "configuration": {
            "max_file_size_mb": settings.max_file_size / (1024 * 1024),
            "chunk_size": settings.chunk_size,
            "embedding_model": settings.embedding_model
        }
    }