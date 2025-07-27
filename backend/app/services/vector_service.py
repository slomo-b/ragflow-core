from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional
import uuid
import logging
from datetime import datetime

from ..core.config import settings

logger = logging.getLogger(__name__)

class VectorService:
    def __init__(self):
        self.client = QdrantClient(
            host=settings.qdrant_host,
            port=settings.qdrant_port
        )
        self.encoder = SentenceTransformer(settings.embedding_model)
        self.collection_name = settings.qdrant_collection_name
        self._ensure_collection()
    
    def _ensure_collection(self):
        """Create Qdrant collection if it doesn't exist"""
        try:
            collections = self.client.get_collections().collections
            collection_exists = any(c.name == self.collection_name for c in collections)
            
            if not collection_exists:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=384,  # all-MiniLM-L6-v2 dimension
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Created Qdrant collection: {self.collection_name}")
            else:
                logger.info(f"Qdrant collection already exists: {self.collection_name}")
                
        except Exception as e:
            logger.error(f"Error creating Qdrant collection: {e}")
            raise
    
    async def add_document_chunks(self, document_id: str, chunks: List[str]) -> List[str]:
        """Add document chunks to vector store and return point IDs"""
        points = []
        point_ids = []
        
        logger.info(f"Adding {len(chunks)} chunks for document {document_id}")
        
        for i, chunk in enumerate(chunks):
            # Generate unique point ID
            point_id = str(uuid.uuid4())
            
            # Generate embedding
            vector = self.encoder.encode(chunk).tolist()
            
            # Create point with metadata
            points.append(PointStruct(
                id=point_id,
                vector=vector,
                payload={
                    "document_id": document_id,
                    "chunk_index": i,
                    "text": chunk,
                    "timestamp": datetime.utcnow().isoformat(),
                    "embedding_model": settings.embedding_model
                }
            ))
            point_ids.append(point_id)
        
        # Batch insert to Qdrant
        try:
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            logger.info(f"Successfully added {len(points)} vectors to Qdrant")
            return point_ids
            
        except Exception as e:
            logger.error(f"Error adding vectors to Qdrant: {e}")
            raise
    
    def search(
        self, 
        query: str, 
        top_k: int = 5, 
        document_ids: Optional[List[str]] = None,
        score_threshold: float = 0.0
    ) -> List[Dict[str, Any]]:
        """Semantic search for relevant chunks"""
        
        # Generate query embedding
        query_vector = self.encoder.encode(query).tolist()
        
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
                query_vector=query_vector,
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
            
            logger.info(f"Search completed: {len(formatted_results)} results for query '{query[:50]}...'")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error performing vector search: {e}")
            raise
    
    def delete_document_vectors(self, document_id: str) -> bool:
        """Delete all vectors for a specific document"""
        try:
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
            logger.info(f"Deleted all vectors for document {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting document vectors: {e}")
            return False

    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the vector collection"""
        try:
            info = self.client.get_collection(self.collection_name)
            return {
                "name": self.collection_name,
                "vectors_count": info.vectors_count,
                "indexed_vectors_count": info.indexed_vectors_count,
                "points_count": info.points_count
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return {}