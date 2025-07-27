from sqlalchemy import Column, String, Text, DateTime, JSON, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from ..core.database import Base

class Collection(Base):
    __tablename__ = "collections"
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Collection Information
    name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Statistics
    documents_count = Column(Integer, default=0)
    total_chunks = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    meta_data = Column(JSON, default=dict)
    
    # Relationships
    documents = relationship("Document", back_populates="collection")
    
    def __repr__(self):
        return f"<Collection(id={self.id}, name='{self.name}', documents={self.documents_count})>"