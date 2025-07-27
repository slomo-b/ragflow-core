# backend/app/models/conversation.py
from sqlalchemy import Column, String, Text, DateTime, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from . import Base

class Conversation(Base):
    __tablename__ = "conversations"
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Conversation Information
    title = Column(String(255))
    
    # Content
    messages = Column(JSON, default=list)  # List of messages with role, content, timestamp
    
    # Context
    context_documents = Column(JSON, default=list)  # Document IDs used in conversation
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Conversation(id={self.id}, title='{self.title}')>"
