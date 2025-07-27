from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID

from .document import DocumentResponse

class CollectionBase(BaseModel):
    name: str
    description: Optional[str] = None

class CollectionCreate(CollectionBase):
    pass

class CollectionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    meta_data: Optional[Dict[str, Any]] = None  # CHANGED: metadata -> meta_data

class CollectionInDB(CollectionBase):
    id: UUID
    documents_count: int
    total_chunks: int
    created_at: datetime
    updated_at: datetime
    meta_data: Dict[str, Any]  # CHANGED: metadata -> meta_data
    
    class Config:
        from_attributes = True

class CollectionResponse(CollectionInDB):
    pass

class CollectionWithDocuments(CollectionResponse):
    documents: List[DocumentResponse]
