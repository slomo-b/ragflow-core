from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
import time

from ....core.database import get_db
from ....core.config import settings
from ....services.vector_service import VectorService

router = APIRouter()

@router.get("/")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": settings.version
    }

@router.get("/ready")
async def readiness_check(db: Session = Depends(get_db)):
    """Comprehensive readiness check"""
    checks = {}
    overall_status = "healthy"
    
    # Database check
    try:
        db.execute("SELECT 1")
        checks["database"] = {"status": "healthy", "message": "Connected"}
    except Exception as e:
        checks["database"] = {"status": "unhealthy", "message": str(e)}
        overall_status = "unhealthy"
    
    # Vector database check
    try:
        vector_service = VectorService()
        collection_info = vector_service.get_collection_info()
        checks["vector_db"] = {
            "status": "healthy", 
            "message": "Connected",
            "collection_info": collection_info
        }
    except Exception as e:
        checks["vector_db"] = {"status": "unhealthy", "message": str(e)}
        overall_status = "unhealthy"
    
    # File storage check
    try:
        if settings.upload_dir.exists() and settings.upload_dir.is_dir():
            checks["file_storage"] = {"status": "healthy", "message": "Directory accessible"}
        else:
            checks["file_storage"] = {"status": "unhealthy", "message": "Upload directory not accessible"}
            overall_status = "unhealthy"
    except Exception as e:
        checks["file_storage"] = {"status": "unhealthy", "message": str(e)}
        overall_status = "unhealthy"
    
    response = {
        "status": overall_status,
        "timestamp": time.time(),
        "version": settings.version,
        "checks": checks
    }
    
    if overall_status == "unhealthy":
        raise HTTPException(status_code=503, detail=response)
    
    return response

@router.get("/info")
async def system_info():
    """System information"""
    return {
        "app_name": settings.app_name,
        "version": settings.version,
        "debug": settings.debug,
        "embedding_model": settings.embedding_model,
        "max_file_size_mb": settings.max_file_size / (1024 * 1024),
        "allowed_file_types": settings.allowed_file_types,
        "chunk_size": settings.chunk_size,
        "chunk_overlap": settings.chunk_overlap,
        "top_k_default": settings.top_k
    }