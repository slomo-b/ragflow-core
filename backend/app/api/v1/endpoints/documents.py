from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import Optional

from ....core.database import get_db
from ....services.document_service import DocumentService
from ....schemas.document import DocumentResponse, DocumentListResponse

router = APIRouter()

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    collection_id: Optional[str] = Query(None, description="Collection ID to add document to"),
    db: Session = Depends(get_db)
):
    """
    Upload and process a document
    
    - **file**: The document file to upload (PDF, DOCX, TXT, MD, HTML)
    - **collection_id**: Optional collection ID (uses default collection if not provided)
    """
    service = DocumentService(db)
    return await service.upload_document(file, collection_id)

@router.get("/", response_model=DocumentListResponse)
async def list_documents(
    skip: int = Query(0, ge=0, description="Number of documents to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of documents to return"),
    collection_id: Optional[str] = Query(None, description="Filter by collection ID"),
    db: Session = Depends(get_db)
):
    """
    List documents with pagination
    
    - **skip**: Number of documents to skip (for pagination)
    - **limit**: Maximum number of documents to return
    - **collection_id**: Optional filter by collection
    """
    service = DocumentService(db)
    return service.get_documents(skip=skip, limit=limit, collection_id=collection_id)

@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific document by ID
    """
    service = DocumentService(db)
    document = service.get_document(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document

@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete a document and its associated vectors
    """
    service = DocumentService(db)
    success = service.delete_document(document_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found or could not be deleted")
    return {"message": "Document deleted successfully"}

@router.get("/{document_id}/content")
async def get_document_content(
    document_id: str,
    db: Session = Depends(get_db)
):
    """
    Get the extracted text content of a document
    """
    service = DocumentService(db)
    document = service.get_document(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if document.status != "completed":
        raise HTTPException(status_code=400, detail=f"Document processing not completed (status: {document.status})")
    
    return {"content": document.content}