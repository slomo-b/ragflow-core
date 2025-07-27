from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

class DocumentBase(BaseModel):
    filename: str
    content_type: str
    file_size: int
    collection_id: Optional[UUID] = None

class DocumentCreate(DocumentBase):
    pass

class DocumentUpdate(BaseModel):
    filename: Optional[str] = None
    collection_id: Optional[UUID] = None
    meta_data: Optional[Dict[str, Any]] = None

class DocumentInDB(DocumentBase):
    id: UUID
    original_filename: str
    file_path: Optional[str] = None
    content: Optional[str] = None
    status: str
    error_message: Optional[str] = None
    processing_started_at: Optional[datetime] = None
    processing_completed_at: Optional[datetime] = None
    chunks_count: int
    vector_ids: List[str]
    embedding_model: str
    created_at: datetime
    updated_at: datetime
    meta_data: Dict[str, Any]
    
    class Config:
        from_attributes = True

class DocumentResponse(DocumentInDB):
    pass

class DocumentListResponse(BaseModel):
    documents: List[DocumentResponse]
    total: int
    skip: int
    limit: int