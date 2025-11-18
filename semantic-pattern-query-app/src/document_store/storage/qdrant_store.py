"""
Layer 4: Qdrant Vector Store

Qdrant vector database with healthcare-specific configuration:
- Scalar quantization (4x memory reduction)
- On-disk storage
- Payload filtering for metadata
"""

from typing import List, Dict, Any, Optional
import numpy as np
import os
import logging
import uuid

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import (
        Distance, VectorParams, CollectionStatus,
        PointStruct, Filter, FieldCondition, MatchValue
    )
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False
    QdrantClient = None

from ..processors.semantic_chunker import Chunk

logger = logging.getLogger(__name__)


class HealthcareVectorStore:
    """
    Qdrant vector store with production configuration.
    
    Features:
    - Scalar quantization (4x memory reduction)
    - On-disk storage for large datasets
    - Payload filtering for metadata
    - Multi-tenant support
    """
    
    def __init__(
        self,
        url: Optional[str] = None,
        api_key: Optional[str] = None,
        collection_name: str = "pattern_documents",
        vector_size: int = 384,  # Match local embedding model
        on_disk: bool = True
    ):
        """
        Initialize Qdrant vector store.
        
        Args:
            url: Qdrant URL (default: from env or http://localhost:6333)
            api_key: Optional API key
            collection_name: Collection name
            vector_size: Vector dimension size
            on_disk: Use on-disk storage
        """
        if not QDRANT_AVAILABLE:
            raise ImportError(
                "qdrant-client is not installed. "
                "Install it with: pip install qdrant-client"
            )
        
        self.url = url or os.getenv("QDRANT_URL", "http://localhost:6333")
        self.api_key = api_key or os.getenv("QDRANT_API_KEY")
        self.collection_name = collection_name
        self.vector_size = vector_size
        self.on_disk = on_disk
        
        # Initialize client
        client_kwargs = {"url": self.url}
        if self.api_key:
            client_kwargs["api_key"] = self.api_key
        # Disable version check due to version mismatch (client 1.16.0 vs server 1.7.0)
        client_kwargs["prefer_grpc"] = False
        client_kwargs["timeout"] = 30
        try:
            # Try to disable compatibility check
            client_kwargs["check_compatibility"] = False
        except:
            pass
        
        self.client = QdrantClient(**client_kwargs)
        
        # Ensure collection exists
        self._ensure_collection()
        
        logger.info(
            f"HealthcareVectorStore initialized: "
            f"url={self.url}, collection={self.collection_name}"
        )
    
    def _ensure_collection(self):
        """Create collection if it doesn't exist."""
        collections = self.client.get_collections().collections
        collection_names = [c.name for c in collections]
        
        if self.collection_name not in collection_names:
            logger.info(f"Creating collection: {self.collection_name}")
            
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=Distance.COSINE,
                    on_disk=self.on_disk  # CRITICAL for large datasets
                ),
                # Scalar quantization for memory reduction
                quantization_config={
                    "scalar": {
                        "type": "int8",  # 4x memory reduction
                        "quantile": 0.99
                    }
                } if self.on_disk else None
            )
            
            # Create payload indexes for filtering
            self._create_payload_indexes()
        else:
            logger.info(f"Using existing collection: {self.collection_name}")
    
    def _create_payload_indexes(self):
        """Create payload indexes for efficient filtering."""
        indexes = [
            ("document_id", "keyword"),
            ("document_type", "keyword"),
            ("section_type", "keyword"),
            ("source_path", "keyword"),
        ]
        
        for field_name, field_schema in indexes:
            try:
                self.client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name=field_name,
                    field_schema=field_schema
                )
                logger.debug(f"Created payload index: {field_name}")
            except Exception as e:
                logger.warning(f"Could not create index for {field_name}: {e}")
    
    def upsert_documents(
        self,
        chunks: List[Chunk],
        embeddings: np.ndarray
    ):
        """
        Upsert documents with embeddings.
        
        Args:
            chunks: List of Chunk objects
            embeddings: numpy array of embeddings (n_chunks, vector_size)
        """
        if len(chunks) != len(embeddings):
            raise ValueError(
                f"Mismatch: {len(chunks)} chunks but {len(embeddings)} embeddings"
            )
        
        points = []
        
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            # Use consistent chunk ID from metadata (generated by chunker)
            chunk_id_str = chunk.metadata.get("chunk_id")
            if chunk_id_str:
                # Convert string UUID to UUID object
                try:
                    chunk_id = uuid.UUID(chunk_id_str) if isinstance(chunk_id_str, str) else chunk_id_str
                except (ValueError, AttributeError):
                    # Fallback: generate from source_path + chunk_index for consistency
                    source_path = chunk.metadata.get("source_path", "")
                    chunk_index = chunk.chunk_index
                    import hashlib
                    combined = f"{source_path}:{chunk_index}"
                    hash_bytes = hashlib.md5(combined.encode()).digest()[:16]
                    chunk_id = uuid.UUID(bytes=hash_bytes)
            else:
                # Fallback: generate from source_path + chunk_index
                source_path = chunk.metadata.get("source_path", "")
                chunk_index = chunk.chunk_index
                import hashlib
                combined = f"{source_path}:{chunk_index}"
                hash_bytes = hashlib.md5(combined.encode()).digest()[:16]
                chunk_id = uuid.UUID(bytes=hash_bytes)
            
            # Prepare payload
            payload = {
                "text": chunk.text,
                "document_id": chunk.metadata.get("document_id", ""),
                "document_type": chunk.metadata.get("document_type", "unknown"),
                "section_type": chunk.metadata.get("section_type", "text"),
                "source_path": chunk.metadata.get("source_path", ""),
                "chunk_index": chunk.chunk_index,
                "start_char": chunk.start_char,
                "end_char": chunk.end_char,
            }
            
            # Add any additional metadata
            for key, value in chunk.metadata.items():
                if key not in payload and isinstance(value, (str, int, float, bool)):
                    payload[key] = value
            
            point = PointStruct(
                id=chunk_id,
                vector=embedding.tolist(),
                payload=payload
            )
            points.append(point)
        
        # Batch upsert - for server 1.7.0, use individual point upserts if batch fails
        try:
            # Try standard batch upsert
            operation_info = self.client.upsert(
                collection_name=self.collection_name,
                points=points,
                wait=True
            )
        except Exception as e:
            # For server 1.7.0 compatibility, try upserting points individually
            logger.warning(f"Batch upsert failed, trying individual upserts: {e}")
            try:
                for point in points:
                    self.client.upsert(
                        collection_name=self.collection_name,
                        points=[point],  # Single point
                        wait=False  # Don't wait for each individual point
                    )
                # Wait for all to complete
                import time
                time.sleep(0.5)
            except Exception as e2:
                logger.error(f"Individual upsert also failed: {e2}")
                raise
        
        logger.info(f"Upserted {len(points)} documents to collection")
    
    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search with payload filtering.
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            filters: Optional metadata filters
            
        Returns:
            List of result dictionaries with text, score, and metadata
        """
        # Build filter
        query_filter = None
        if filters:
            conditions = []
            
            for key, value in filters.items():
                if value is not None:
                    conditions.append(
                        FieldCondition(
                            key=key,
                            match=MatchValue(value=value)
                        )
                    )
            
            if conditions:
                query_filter = Filter(must=conditions)
        
        # Search - use search API for server 1.7.0 compatibility
        # Server 1.7.0 doesn't support query_points endpoint
        try:
            # Try the search method (older API)
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding.tolist(),
                query_filter=query_filter,
                limit=top_k
            )
        except AttributeError:
            # Fallback: use query_points if available (newer servers)
            query_result = self.client.query_points(
                collection_name=self.collection_name,
                query=query_embedding.tolist(),
                query_filter=query_filter,
                limit=top_k
            )
            results = query_result.points
        
        # Format results
        formatted_results = []
        for result in results:
            # Handle both old and new API response formats
            if hasattr(result, 'payload'):
                payload = result.payload
                score = result.score
                result_id = result.id
            else:
                # New API format
                payload = getattr(result, 'payload', {})
                score = getattr(result, 'score', 0.0)
                result_id = getattr(result, 'id', None)
            
            formatted_results.append({
                "text": payload.get("text", "") if isinstance(payload, dict) else "",
                "score": float(score),
                "metadata": {
                    k: v for k, v in (payload.items() if isinstance(payload, dict) else {})
                    if k != "text"
                },
                "id": result_id
            })
        
        return formatted_results
    
    def get_collection_info(self) -> Dict[str, Any]:
        """
        Get information about the collection.
        
        Returns:
            Dictionary with collection statistics
        """
        collection_info = self.client.get_collection(self.collection_name)
        
        return {
            "collection_name": self.collection_name,
            "points_count": collection_info.points_count,
            "vectors_count": getattr(collection_info, 'vectors_count', collection_info.points_count),  # Fallback to points_count
            "config": {
                "vector_size": collection_info.config.params.vectors.size,
                "distance": collection_info.config.params.vectors.distance,
                "on_disk": getattr(
                    collection_info.config.params.vectors,
                    "on_disk",
                    False
                )
            }
        }
    
    def delete_by_document_id(self, document_id: str) -> int:
        """
        Delete all points for a specific document.
        
        Args:
            document_id: Document ID to delete
            
        Returns:
            Number of points deleted
        """
        from qdrant_client.models import Filter, FieldCondition, MatchValue
        
        # Build filter for document_id
        query_filter = Filter(
            must=[
                FieldCondition(
                    key="document_id",
                    match=MatchValue(value=document_id)
                )
            ]
        )
        
        # Scroll to find all points with this document_id
        deleted_count = 0
        try:
            # Use scroll to get all points matching the filter
            scroll_result = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=query_filter,
                limit=100,
                with_payload=True,
                with_vectors=False
            )
            
            point_ids = [point.id for point in scroll_result[0]]
            
            while point_ids:
                # Delete batch of points
                self.client.delete(
                    collection_name=self.collection_name,
                    points_selector=point_ids
                )
                deleted_count += len(point_ids)
                
                # Continue scrolling if there are more
                if len(scroll_result[0]) == 100:
                    scroll_result = self.client.scroll(
                        collection_name=self.collection_name,
                        scroll_filter=query_filter,
                        limit=100,
                        offset=len(point_ids),
                        with_payload=True,
                        with_vectors=False
                    )
                    point_ids = [point.id for point in scroll_result[0]]
                else:
                    break
            
            logger.info(f"Deleted {deleted_count} points for document_id: {document_id}")
        except Exception as e:
            logger.error(f"Error deleting points for document_id {document_id}: {e}")
        
        return deleted_count
    
    def delete_by_source_path(self, source_path: str) -> int:
        """
        Delete all points for a specific source path.
        
        Args:
            source_path: Source path to delete
            
        Returns:
            Number of points deleted
        """
        from qdrant_client.models import Filter, FieldCondition, MatchValue
        
        # Build filter for source_path
        query_filter = Filter(
            must=[
                FieldCondition(
                    key="source_path",
                    match=MatchValue(value=source_path)
                )
            ]
        )
        
        # Scroll to find all points with this source_path
        deleted_count = 0
        try:
            # Use scroll to get all points matching the filter
            scroll_result = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=query_filter,
                limit=100,
                with_payload=True,
                with_vectors=False
            )
            
            point_ids = [point.id for point in scroll_result[0]]
            
            while point_ids:
                # Delete batch of points
                self.client.delete(
                    collection_name=self.collection_name,
                    points_selector=point_ids
                )
                deleted_count += len(point_ids)
                
                # Continue scrolling if there are more
                if len(scroll_result[0]) == 100:
                    scroll_result = self.client.scroll(
                        collection_name=self.collection_name,
                        scroll_filter=query_filter,
                        limit=100,
                        offset=len(point_ids),
                        with_payload=True,
                        with_vectors=False
                    )
                    point_ids = [point.id for point in scroll_result[0]]
                else:
                    break
            
            logger.info(f"Deleted {deleted_count} points for source_path: {source_path}")
        except Exception as e:
            logger.error(f"Error deleting points for source_path {source_path}: {e}")
        
        return deleted_count
    
    def delete_collection(self):
        """Delete the collection."""
        self.client.delete_collection(collection_name=self.collection_name)
        logger.info(f"Deleted collection: {self.collection_name}")

