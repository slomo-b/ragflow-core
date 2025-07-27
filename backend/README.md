# RagFlow Backend

Open Source RAG Platform Backend - FastAPI + PostgreSQL + Qdrant

## Features

- 📄 **Document Upload**: PDF, DOCX, TXT, MD, HTML
- 🔍 **Vector Search**: Semantic search with Qdrant
- 🗄️ **Database**: PostgreSQL with SQLAlchemy
- 🏗️ **Collections**: Organize documents
- 🚀 **Background Processing**: Async document processing
- 📚 **API Documentation**: Auto-generated Swagger UI

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run with Docker Compose
docker compose -f docker/docker-compose.dev.yml up -d

# Run locally
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000