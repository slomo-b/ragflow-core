from pydantic_settings import BaseSettings
from pathlib import Path
from typing import Optional, List

class Settings(BaseSettings):
    # App Configuration
    app_name: str = "RagFlow"
    debug: bool = True
    version: str = "1.0.0"
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Database Configuration
    database_url: str = "postgresql://ragflow:ragflow@postgres:5432/ragflow"
    
    # Vector Database Configuration
    qdrant_host: str = "qdrant"
    qdrant_port: int = 6333
    qdrant_collection_name: str = "documents"
    
    # Redis Configuration
    redis_url: str = "redis://redis:6379/0"
    
    # AI APIs
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    
    # File Storage
    upload_dir: Path = Path("/app/uploads")
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    allowed_file_types: List[str] = [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain",
        "text/markdown",
        "text/html"
    ]
    
    # RAG Configuration
    chunk_size: int = 1000
    chunk_overlap: int = 200
    top_k: int = 5
    embedding_model: str = "all-MiniLM-L6-v2"
    
    # Processing
    max_concurrent_uploads: int = 5
    processing_timeout: int = 300  # 5 minutes
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure upload directory exists
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()