from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .core.config import settings
from .api.v1.router import api_router
from .core.database import engine
from .models import Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting RagFlow Backend...")
    yield
    # Shutdown
    print("👋 Shutting down RagFlow Backend...")

app = FastAPI(
    title="RagFlow API",
    version="1.0.0",
    description="Open Source RAG Platform",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "RagFlow API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}