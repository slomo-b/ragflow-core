from sqlalchemy import Column, String, Integer, Text, DateTime, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from ..core.database import Base

class Document(Base):
    __tablename__ = "documents"
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # File Information
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    content_type = Column(String(100), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_path = Column(String(500))  # Local file storage path
    
    # Content
    content = Column(Text)  # Extracted text content
    
    # Processing Status
    status = Column(String(50), default="pending")  # pending, processing, completed, failed
    error_message = Column(Text)
    processing_started_at = Column(DateTime)
    processing_completed_at = Column(DateTime)
    
    # Vector Information
    chunks_count = Column(Integer, default=0)
    vector_ids = Column(JSON, default=list)  # List of Qdrant point IDs
    embedding_model = Column(String(100), default="all-MiniLM-L6-v2")
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    meta_data = Column(JSON, default=dict)
    
    # Relationships
    collection_id = Column(UUID(as_uuid=True), ForeignKey("collections.id"), nullable=True)
    collection = relationship("Collection", back_populates="documents")
    
    def __repr__(self):
        return f"<Document(id={self.id}, filename='{self.filename}', status='{self.status}')>"