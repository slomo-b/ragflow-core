from pydantic_settings import BaseSettings
from pathlib import Path
from typing import Optional

class Settings(BaseSettings):
    # App
    app_name: str = "RagFlow"
    debug: bool = True
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Database
    database_url: str = "postgresql://ragflow:ragflow@localhost:5432/ragflow"
    
    # Vector Database
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    
    # AI APIs
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    
    # Files
    upload_dir: Path = Path("uploads")
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    
    # RAG
    chunk_size: int = 1000
    chunk_overlap: int = 200
    top_k: int = 5
    
    class Config:
        env_file = ".env"

settings = Settings()