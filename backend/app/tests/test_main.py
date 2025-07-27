import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import get_db, Base

# Test database
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

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "RagFlow API"
    assert "version" in data

def test_ping():
    response = client.get("/ping")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "pong"

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_health_v1():
    response = client.get("/api/v1/health/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_documents_list():
    response = client.get("/api/v1/documents/")
    assert response.status_code == 200
    data = response.json()
    assert "documents" in data
    assert "total" in data

def test_collections_list():
    response = client.get("/api/v1/collections/")
    assert response.status_code == 200
    data = response.json()
    assert "collections" in data

def test_routes_endpoint():
    response = client.get("/api/v1/dev/routes")
    assert response.status_code == 200
    data = response.json()
    assert "routes" in data
    assert "total_routes" in data