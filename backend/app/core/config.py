from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # App
    app_name: str = "RagFlow"
    debug: bool = True
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Database (optional for now)
    database_url: Optional[str] = None
    
    # Vector Database (optional for now)
    qdrant_host: str = "qdrant"
    qdrant_port: int = 6333
    
    class Config:
        env_file = ".env"

settings = Settings()
