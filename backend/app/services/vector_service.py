# File: backend/app/services/vector_service.py
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
import logging
import asyncio

from ..core.config import settings

logger = logging.getLogger(__name__)

class VectorService:
    def __init__(self):
        self.client = QdrantClient(
            host=settings.qdrant_host,
            port=settings.qdrant_port
        )
        self.encoder = SentenceTransformer(settings.embedding_model)
        self.collection_name = "documents"
        self._ensure_collection()
    
    def _ensure_collection(self):
        """Create collection if it doesn't exist"""
        try:
            collections = self.client.get_collections().collections
            if not any(c.name == self.collection_name for c in collections):
                logger.info(f"Creating Qdrant collection: {self.collection_name}")
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=384,  # all-MiniLM-L6-v2 dimension
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Collection {self.collection_name} created successfully")
            else:
                logger.info(f"Collection {self.collection_name} already exists")
        except Exception as e:
            logger.error(f"Error creating Qdrant collection: {e}")
            raise
    
    async def add_document_chunks(self, document_id: str, chunks: List[str]) -> List[str]:
        """Add document chunks to vector store and return point IDs"""
        logger.info(f"Adding {len(chunks)} chunks for document {document_id}")
        
        points = []
        point_ids = []
        
        # Process chunks in batches to avoid memory issues
        batch_size = 10
        for i in range(0, len(chunks), batch_size):
            batch_chunks = chunks[i:i + batch_size]
            batch_points = []
            batch_ids = []
            
            for j, chunk in enumerate(batch_chunks):
                # Generate unique point ID
                point_id = str(uuid.uuid4())
                
                # Generate embedding (this is CPU intensive, so we run it in executor)
                loop = asyncio.get_event_loop()
                vector = await loop.run_in_executor(None, self.encoder.encode, chunk)
                
                # Create point with metadata
                batch_points.append(PointStruct(
                    id=point_id,
                    vector=vector.tolist(),
                    payload={
                        "document_id": document_id,
                        "chunk_index": i + j,
                        "text": chunk,
                        "timestamp": datetime.utcnow().isoformat(),
                        "embedding_model": settings.embedding_model
                    }
                ))
                batch_ids.append(point_id)
            
            # Insert batch to Qdrant
            try:
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=batch_points,
                    wait=True  # Wait for operation to complete
                )
                logger.info(f"Successfully added batch {i//batch_size + 1} ({len(batch_points)} vectors)")
                points.extend(batch_points)
                point_ids.extend(batch_ids)
                
            except Exception as e:
                logger.error(f"Error adding batch to Qdrant: {e}")
                raise
        
        logger.info(f"Successfully added all {len(points)} vectors to Qdrant")
        return point_ids
    
    async def search(
        self, 
        query: str, 
        top_k: int = 5, 
        document_ids: Optional[List[str]] = None,
        score_threshold: float = 0.0
    ) -> List[Dict[str, Any]]:
        """Semantic search for relevant chunks"""
        
        logger.info(f"Searching for: '{query}' (top_k={top_k})")
        
        # Generate query embedding
        loop = asyncio.get_event_loop()
        query_vector = await loop.run_in_executor(None, self.encoder.encode, query)
        
        # Build filter if document_ids specified
        query_filter = None
        if document_ids:
            query_filter = Filter(
                must=[
                    FieldCondition(
                        key="document_id",
                        match=MatchValue(value=doc_id)
                    ) for doc_id in document_ids
                ]
            )
        
        try:
            # Perform search
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector.tolist(),
                query_filter=query_filter,
                limit=top_k,
                score_threshold=score_threshold
            )
            
            # Format results
            formatted_results = []
            for hit in results:
                formatted_results.append({
                    "id": hit.id,
                    "score": hit.score,
                    "document_id": hit.payload["document_id"],
                    "text": hit.payload["text"],
                    "chunk_index": hit.payload["chunk_index"],
                    "timestamp": hit.payload.get("timestamp"),
                    "embedding_model": hit.payload.get("embedding_model")
                })
            
            logger.info(f"Found {len(formatted_results)} results")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching in Qdrant: {e}")
            raise
    
    def delete_document_vectors(self, document_id: str) -> bool:
        """Delete all vectors for a document"""
        try:
            # Delete points by document_id
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=Filter(
                    must=[
                        FieldCondition(
                            key="document_id",
                            match=MatchValue(value=document_id)
                        )
                    ]
                )
            )
            logger.info(f"Deleted vectors for document: {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting vectors for document {document_id}: {e}")
            return False
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get collection information"""
        try:
            info = self.client.get_collection(self.collection_name)
            return {
                "name": self.collection_name,
                "vectors_count": info.vectors_count,
                "indexed_vectors_count": info.indexed_vectors_count,
                "points_count": info.points_count,
                "status": info.status
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return {}