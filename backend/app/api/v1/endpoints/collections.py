from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ....core.database import get_db
from ....models.collection import Collection
from ....schemas.document import DocumentResponse

router = APIRouter()

@router.post("/")
async def create_collection(
    name: str,
    description: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Create a new collection"""
    collection = Collection(
        name=name,
        description=description
    )
    
    db.add(collection)
    db.commit()
    db.refresh(collection)
    
    return {
        "id": str(collection.id),
        "name": collection.name,
        "description": collection.description,
        "documents_count": collection.documents_count,
        "created_at": collection.created_at.isoformat()
    }

@router.get("/")
async def list_collections(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """List all collections"""
    collections = db.query(Collection).offset(skip).limit(limit).all()
    total = db.query(Collection).count()
    
    return {
        "collections": [
            {
                "id": str(collection.id),
                "name": collection.name,
                "description": collection.description,
                "documents_count": collection.documents_count,
                "total_chunks": collection.total_chunks,
                "created_at": collection.created_at.isoformat()
            }
            for collection in collections
        ],
        "total": total,
        "skip": skip,
        "limit": limit
    }

@router.get("/{collection_id}")
async def get_collection(
    collection_id: str,
    include_documents: bool = Query(False, description="Include documents in response"),
    db: Session = Depends(get_db)
):
    """Get collection by ID"""
    collection = db.query(Collection).filter(Collection.id == collection_id).first()
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    result = {
        "id": str(collection.id),
        "name": collection.name,
        "description": collection.description,
        "documents_count": collection.documents_count,
        "total_chunks": collection.total_chunks,
        "created_at": collection.created_at.isoformat(),
        "updated_at": collection.updated_at.isoformat()
    }
    
    if include_documents:
        documents = []
        for doc in collection.documents:
            documents.append({
                "id": str(doc.id),
                "filename": doc.filename,
                "status": doc.status,
                "created_at": doc.created_at.isoformat()
            })
        result["documents"] = documents
    
    return result

@router.put("/{collection_id}")
async def update_collection(
    collection_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Update collection"""
    collection = db.query(Collection).filter(Collection.id == collection_id).first()
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    if name is not None:
        collection.name = name
    if description is not None:
        collection.description = description
    
    db.commit()
    db.refresh(collection)
    
    return {
        "id": str(collection.id),
        "name": collection.name,
        "description": collection.description,
        "updated_at": collection.updated_at.isoformat()
    }

@router.delete("/{collection_id}")
async def delete_collection(
    collection_id: str,
    force: bool = Query(False, description="Force delete even if collection has documents"),
    db: Session = Depends(get_db)
):
    """Delete collection"""
    collection = db.query(Collection).filter(Collection.id == collection_id).first()
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    # Check if collection has documents
    if collection.documents_count > 0 and not force:
        raise HTTPException(
            status_code=400, 
            detail=f"Collection has {collection.documents_count} documents. Use force=true to delete anyway."
        )
    
    db.delete(collection)
    db.commit()
    
    return {"message": "Collection deleted successfully"}