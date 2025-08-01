# File: backend/app/core/config.py
from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Application Settings
    app_name: str = "RagFlow"
    version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"
    
    # API Settings
    api_v1_prefix: str = "/api/v1"
    
    # Database Settings
    postgres_user: str = "ragflow"
    postgres_password: str = "ragflow"
    postgres_db: str = "ragflow"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    
    # Vector Database Settings (Qdrant)
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection_name: str = "documents"
    
    # Redis Settings
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    
    # LLM API Settings
    # Google Gemini (Required for cloud LLM)
    google_api_key: Optional[str] = None
    gemini_model: str = "gemini-2.0-flash-exp"
    
    # Ollama Settings (Optional - only used if Ollama is running externally)
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"
    
    # File Upload Settings
    max_file_size_mb: int = 50
    upload_path: str = "./uploads"
    allowed_file_types: list = [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document", 
        "text/plain",
        "text/markdown",
        "text/html"
    ]
    
    # Document Processing Settings
    chunk_size: int = 1000
    chunk_overlap: int = 200
    max_chunks_per_document: int = 1000
    
    # Embedding Settings
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_dimension: int = 384
    
    # RAG Settings
    max_context_chunks: int = 5
    max_context_length: int = 4000
    chunk_overlap_threshold: float = 0.8
    default_temperature: float = 0.7
    default_max_tokens: int = 1000
    
    # Security Settings
    secret_key: str = "your-secret-key-change-in-production"
    access_token_expire_minutes: int = 30
    
    # CORS Settings
    allowed_origins: list = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ]
    
    # Logging Settings
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Background Task Settings
    celery_broker_url: Optional[str] = None
    celery_result_backend: Optional[str] = None
    
    # Health Check Settings
    health_check_interval: int = 30
    
    @property
    def database_url(self) -> str:
        """PostgreSQL database URL"""
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    
    @property
    def async_database_url(self) -> str:
        """Async PostgreSQL database URL"""
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    
    @property
    def redis_url(self) -> str:
        """Redis connection URL"""
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"
    
    @property
    def qdrant_url(self) -> str:
        """Qdrant connection URL"""
        return f"http://{self.qdrant_host}:{self.qdrant_port}"
    
    @property
    def upload_directory(self) -> str:
        """Full path to upload directory"""
        upload_dir = os.path.abspath(self.upload_path)
        os.makedirs(upload_dir, exist_ok=True)
        return upload_dir
    
    @property
    def max_file_size_bytes(self) -> int:
        """Max file size in bytes"""
        return self.max_file_size_mb * 1024 * 1024
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.environment.lower() in ["development", "dev"]
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.environment.lower() in ["production", "prod"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ignore extra environment variables

# Create settings instance
settings = Settings()

def validate_settings():
    """Validate critical settings at startup"""
    errors = []
    warnings = []
    
    # Critical validations
    if not settings.secret_key or settings.secret_key == "your-secret-key-change-in-production":
        if settings.is_production:
            errors.append("SECRET_KEY must be set in production")
        else:
            warnings.append("Using default SECRET_KEY (change for production)")
    
    # LLM validations
    if not settings.google_api_key:
        warnings.append("GOOGLE_API_KEY not set - Gemini will not be available")
    
    # Database validations
    if not all([settings.postgres_user, settings.postgres_password, settings.postgres_db]):
        errors.append("PostgreSQL credentials are incomplete")
    
    # File upload validations
    if settings.max_file_size_mb <= 0:
        errors.append("MAX_FILE_SIZE_MB must be positive")
    
    if settings.max_file_size_mb > 100:
        warnings.append(f"Large file size limit: {settings.max_file_size_mb}MB")
    
    # Print results
    if errors:
        print("❌ Configuration Errors:")
        for error in errors:
            print(f"   • {error}")
        raise ValueError("Invalid configuration - cannot start")
    
    if warnings:
        print("⚠️  Configuration Warnings:")
        for warning in warnings:
            print(f"   • {warning}")
    
    # Info about optional services
    print("💡 Optional Services:")
    print(f"   • Ollama: Will be used if available at {settings.ollama_url}")
    print(f"   • Celery: {'Enabled' if settings.celery_broker_url else 'Disabled (background tasks will run synchronously)'}")
    
    print(f"✅ Configuration validated for {settings.environment.upper()} environment")

def get_settings() -> Settings:
    """Get settings instance (useful for dependency injection)"""
    return settings

# Validate settings on import
validate_settings()