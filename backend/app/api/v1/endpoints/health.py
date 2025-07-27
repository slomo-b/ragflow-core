from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

@router.get("/")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "ragflow-backend"
    }

@router.get("/ready")
async def readiness_check():
    # TODO: Add database and vector store connectivity checks
    return {
        "status": "ready",
        "timestamp": datetime.utcnow().isoformat()
    }
