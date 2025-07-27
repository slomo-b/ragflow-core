# RagFlow - Open Source RAG Platform

## 🚀 Quick Start

### Development Environment

```bash
# Start all services
python scripts/start_dev.py

# Or manually:
docker compose -f docker/docker-compose.dev.yml up --build -d
```

### Available Services

- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Frontend**: http://localhost:3000
- **Qdrant**: http://localhost:6333/dashboard

### Health Checks

```bash
# Check backend
curl http://localhost:8000/ping

# Check API health
curl http://localhost:8000/api/v1/health/
```

## 📁 Project Structure

```
ragflow-core/
├── backend/           # FastAPI backend
│   ├── app/          # Application code
│   │   └── main.py   # FastAPI app
│   ├── requirements.txt
│   └── Dockerfile.dev
├── docker/           # Docker configuration
│   └── docker-compose.dev.yml
├── scripts/          # Utility scripts
│   └── start_dev.py
└── README.md
```

## 🎯 Current Status

✅ **Phase 1 Complete**: Backend foundation ready
🔄 **Phase 2 Ready**: Core features implementation can begin

## 🔧 Development Commands

```bash
# View logs
docker compose -f docker/docker-compose.dev.yml logs -f

# Restart services
docker compose -f docker/docker-compose.dev.yml restart

# Stop services
docker compose -f docker/docker-compose.dev.yml down

# Rebuild backend
docker compose -f docker/docker-compose.dev.yml up --build backend -d
```

## 📈 Next Steps

Ready for Phase 2 implementation:
- Document Upload API
- Vector Search Service
- Frontend UI Components
- LLM Integration


# Phase 2 Deployment Guide

## 🚀 Phase 2 Features
- ✅ Document Upload (PDF, DOCX, TXT, MD, HTML)
- ✅ Text Processing & Chunking
- ✅ Vector Embeddings (sentence-transformers)
- ✅ Semantic Search (Qdrant)
- ✅ Database Models (PostgreSQL)
- ✅ Background Processing
- ✅ Health Monitoring

## 📦 Updated Dependencies
The requirements.txt now includes all Phase 2 dependencies.

## 🔄 Restart Instructions
After updating all files:

```bash
# Stop current containers
docker compose -f docker/docker-compose.dev.yml down

# Rebuild with new dependencies
docker compose -f docker/docker-compose.dev.yml up --build -d

# Test the system
python test_phase2.py
```

## 🧪 Testing
- Upload documents: `POST /api/v1/documents/upload`
- List documents: `GET /api/v1/documents/`
- Search: `POST /api/v1/search/semantic`
- Health: `GET /api/v1/health/ready`

## 📊 API Documentation
Visit http://localhost:8000/docs for complete API documentation.