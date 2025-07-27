# backend/app/tests/test_document_upload.py
import pytest
import asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import tempfile
import os

from ..main import app
from ..core.database import get_db
from ..models import Base

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

def test_upload_text_document():
    """Test uploading a text document"""
    # Create temporary text file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("This is a test document for the RAG system.")
        temp_file_path = f.name
    
    try:
        with open(temp_file_path, 'rb') as f:
            response = client.post(
                "/api/v1/documents/upload",
                files={"file": ("test.txt", f, "text/plain")}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["filename"] == "test.txt"
        assert data["status"] == "pending"
        assert data["content_type"] == "text/plain"
        
    finally:
        os.unlink(temp_file_path)

def test_list_documents():
    """Test listing documents"""
    response = client.get("/api/v1/documents/")
    assert response.status_code == 200
    data = response.json()
    assert "documents" in data
    assert "total" in data

def test_search_documents():
    """Test semantic search"""
    search_request = {
        "query": "test document",
        "top_k": 5
    }
    
    response = client.post("/api/v1/search/semantic", json=search_request)
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "query" in data
    assert data["query"] == "test document"