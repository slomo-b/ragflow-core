from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import asyncio
import aiofiles
from pathlib import Path
import logging
from datetime import datetime
import uuid

from ..models.document import Document
from ..models.collection import Collection
from ..schemas.document import DocumentResponse, DocumentListResponse
from ..core.config import settings
from .text_processor import TextProcessor
from .vector_service import VectorService

logger = logging.getLogger(__name__)

class DocumentService:
    def __init__(self, db: Session):
        self.db = db
        self.text_processor = TextProcessor()
        self.vector_service = VectorService()
    
    async def upload_document(
        self, 
        file: UploadFile, 
        collection_id: Optional[str] = None
    ) -> DocumentResponse:
        """Upload and process a document"""
        
        # 1. Validate file
        await self._validate_file(file)
        
        # 2. Get or create collection
        collection = self._get_or_create_collection(collection_id)
        
        # 3. Save file to disk
        file_path = await self._save_file(file)
        
        # 4. Create database record
        document = Document(
            filename=self._sanitize_filename(file.filename),
            original_filename=file.filename,
            content_type=file.content_type,
            file_size=file.size,
            file_path=str(file_path),
            collection_id=collection.id,
            status="pending"
        )
        
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        
        # 5. Start background processing
        asyncio.create_task(self._process_document_async(document.id))
        
        logger.info(f"Document uploaded: {document.filename} (ID: {document.id})")
        return DocumentResponse.from_orm(document)
    
    def get_documents(
        self, 
        skip: int = 0, 
        limit: int = 100,
        collection_id: Optional[str] = None
    ) -> DocumentListResponse:
        """Get list of documents"""
        
        query = self.db.query(Document)
        
        if collection_id:
            query = query.filter(Document.collection_id == collection_id)
        
        total = query.count()
        documents = query.offset(skip).limit(limit).all()
        
        return DocumentListResponse(
            documents=[DocumentResponse.from_orm(doc) for doc in documents],
            total=total,
            skip=skip,
            limit=limit
        )
    
    def get_document(self, document_id: str) -> Optional[DocumentResponse]:
        """Get document by ID"""
        document = self.db.query(Document).filter(Document.id == document_id).first()
        if document:
            return DocumentResponse.from_orm(document)
        return None
    
    def delete_document(self, document_id: str) -> bool:
        """Delete document and its vectors"""
        document = self.db.query(Document).filter(Document.id == document_id).first()
        if not document:
            return False
        
        try:
            # Delete vectors from Qdrant
            if document.vector_ids:
                self.vector_service.delete_document_vectors(str(document.id))
            
            # Delete file from disk
            if document.file_path and Path(document.file_path).exists():
                Path(document.file_path).unlink()
            
            # Delete from database
            self.db.delete(document)
            self.db.commit()
            
            logger.info(f"Document deleted: {document.filename} (ID: {document.id})")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {e}")
            self.db.rollback()
            return False
    
    # Private methods
    
    async def _validate_file(self, file: UploadFile):
        """Validate uploaded file"""
        if file.size > settings.max_file_size:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size: {settings.max_file_size / 1024 / 1024:.1f}MB"
            )
        
        if file.content_type not in settings.allowed_file_types:
            raise HTTPException(
                status_code=415,
                detail=f"File type not supported: {file.content_type}"
            )
    
    async def _save_file(self, file: UploadFile) -> Path:
        """Save uploaded file to disk"""
        # Create unique filename
        file_id = str(uuid.uuid4())
        file_extension = Path(file.filename).suffix
        filename = f"{file_id}{file_extension}"
        file_path = settings.upload_dir / filename
        
        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        return file_path
    
    def _get_or_create_collection(self, collection_id: Optional[str]) -> Collection:
        """Get existing collection or create default one"""
        if collection_id:
            collection = self.db.query(Collection).filter(Collection.id == collection_id).first()
            if not collection:
                raise HTTPException(status_code=404, detail="Collection not found")
            return collection
        
        # Get or create default collection
        default_collection = self.db.query(Collection).filter(
            Collection.name == "Default Collection"
        ).first()
        
        if not default_collection:
            default_collection = Collection(
                name="Default Collection",
                description="Default collection for uploaded documents"
            )
            self.db.add(default_collection)
            self.db.commit()
            self.db.refresh(default_collection)
        
        return default_collection
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for safe storage"""
        # Remove or replace unsafe characters
        safe_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-_"
        sanitized = "".join(c if c in safe_chars else "_" for c in filename)
        return sanitized[:255]  # Limit length
    
    async def _process_document_async(self, document_id: str):
        """Background document processing"""
        try:
            # Update status
            document = self.db.query(Document).filter(Document.id == document_id).first()
            document.status = "processing"
            document.processing_started_at = datetime.utcnow()
            self.db.commit()
            
            # Extract text
            content = await self.text_processor.extract_text(document.file_path)
            
            # Create chunks
            chunks = self.text_processor.chunk_text(content)
            
            # Generate embeddings and store in vector DB
            vector_ids = await self.vector_service.add_document_chunks(
                str(document.id), chunks
            )
            
            # Update document
            document.content = content
            document.chunks_count = len(chunks)
            document.vector_ids = vector_ids
            document.status = "completed"
            document.processing_completed_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Document processed successfully: {document.filename}")
            
        except Exception as e:
            logger.error(f"Error processing document {document_id}: {e}")
            
            # Update status to failed
            document = self.db.query(Document).filter(Document.id == document_id).first()
            if document:
                document.status = "failed"
                document.error_message = str(e)
                document.processing_completed_at = datetime.utcnow()
                self.db.commit()