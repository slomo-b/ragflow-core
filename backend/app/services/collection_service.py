# backend/app/services/collection_service.py
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from ..models.collection import Collection
from ..models.document import Document
from ..schemas.collection import (
    CollectionCreate, 
    CollectionUpdate, 
    CollectionResponse, 
    CollectionWithDocuments
)

logger = logging.getLogger(__name__)

class CollectionService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_collection(self, collection_data: CollectionCreate) -> CollectionResponse:
        """Create a new collection"""
        collection = Collection(
            name=collection_data.name,
            description=collection_data.description
        )
        
        self.db.add(collection)
        self.db.commit()
        self.db.refresh(collection)
        
        logger.info(f"Collection created: {collection.name} (ID: {collection.id})")
        return CollectionResponse.from_orm(collection)
    
    def get_collections(self, skip: int = 0, limit: int = 100) -> List[CollectionResponse]:
        """Get list of collections"""
        collections = self.db.query(Collection).offset(skip).limit(limit).all()
        return [CollectionResponse.from_orm(collection) for collection in collections]
    
    def get_collection(
        self, 
        collection_id: str, 
        include_documents: bool = False
    ) -> Optional[CollectionWithDocuments]:
        """Get collection by ID"""
        collection = self.db.query(Collection).filter(Collection.id == collection_id).first()
        if not collection:
            return None
        
        if include_documents:
            # Load documents for this collection
            documents = self.db.query(Document).filter(
                Document.collection_id == collection_id
            ).all()
            
            return CollectionWithDocuments(
                **collection.__dict__,
                documents=[Document.from_orm(doc) for doc in documents]
            )
        else:
            return CollectionResponse.from_orm(collection)
    
    def update_collection(
        self, 
        collection_id: str, 
        collection_update: CollectionUpdate
    ) -> Optional[CollectionResponse]:
        """Update collection"""
        collection = self.db.query(Collection).filter(Collection.id == collection_id).first()
        if not collection:
            return None
        
        # Update fields
        if collection_update.name is not None:
            collection.name = collection_update.name
        if collection_update.description is not None:
            collection.description = collection_update.description
        if collection_update.metadata is not None:
            collection.metadata = collection_update.metadata
        
        self.db.commit()
        self.db.refresh(collection)
        
        logger.info(f"Collection updated: {collection.name} (ID: {collection.id})")
        return CollectionResponse.from_orm(collection)
    
    def delete_collection(self, collection_id: str, force: bool = False) -> bool:
        """Delete collection"""
        collection = self.db.query(Collection).filter(Collection.id == collection_id).first()
        if not collection:
            return False
        
        # Check if collection has documents
        documents_count = self.db.query(Document).filter(
            Document.collection_id == collection_id
        ).count()
        
        if documents_count > 0 and not force:
            logger.warning(f"Cannot delete collection {collection_id}: has {documents_count} documents")
            return False
        
        # If force delete, remove all documents first
        if force and documents_count > 0:
            documents = self.db.query(Document).filter(
                Document.collection_id == collection_id
            ).all()
            
            for doc in documents:
                self.db.delete(doc)
        
        # Delete collection
        self.db.delete(collection)
        self.db.commit()
        
        logger.info(f"Collection deleted: {collection.name} (ID: {collection.id})")
        return True
