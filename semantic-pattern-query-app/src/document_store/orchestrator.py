"""
Main Orchestrator

Wires all 7 layers together into a complete RAG pipeline.
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import logging
import os
import hashlib

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

from .processors.robust_extractor import RobustDocumentExtractor
from .processors.semantic_chunker import SemanticChunker
from .embeddings.hybrid_embedder import HealthcareHybridEmbedder
from .storage.qdrant_store import HealthcareVectorStore
from .search.two_step_retrieval import TwoStepRetrieval
from .search.bm25_search import BM25Search
from .search.hybrid_retriever import HealthcareHybridRetriever
from .generation.rag_generator import HealthcareRAGGenerator
from .cache.semantic_cache import HealthcareSemanticCache

logger = logging.getLogger(__name__)


class SemanticPatternOrchestrator:
    """
    Main orchestrator for the 7-layer RAG pipeline.
    
    Coordinates:
    - Document extraction and chunking
    - Embedding generation
    - Vector storage
    - Hybrid retrieval
    - Response generation
    - Semantic caching
    """
    
    def __init__(
        self,
        qdrant_url: Optional[str] = None,
        elasticsearch_url: Optional[str] = None,
        redis_host: Optional[str] = None,
        ollama_model: str = "nomic-embed-text",
        ollama_generation_model: str = "qwen3:14b",
        ollama_base_url: str = "http://localhost:11434"
    ):
        """
        Initialize orchestrator with all components.

        Args:
            qdrant_url: Qdrant URL
            elasticsearch_url: Elasticsearch URL
            redis_host: Redis host
            ollama_model: Ollama embedding model name
            ollama_generation_model: Ollama generation/chat model name
            ollama_base_url: Ollama API base URL
        """
        # Layer 1: Document Processing
        self.extractor = RobustDocumentExtractor()
        
        # Layer 2: Semantic Chunking
        self.chunker = SemanticChunker(
            chunk_size=512,
            chunk_overlap=100
        )
        
        # Layer 3: Hybrid Embedding
        query_embedder_type = os.getenv("QUERY_EMBEDDER_TYPE", "ollama")
        logger.info(f"Initializing HybridEmbedder with default embedder type: {query_embedder_type}")

        self.embedder = HealthcareHybridEmbedder(
            local_model_name="all-MiniLM-L12-v2",
            qwen_model=ollama_model,
            ollama_base_url=ollama_base_url,
            query_embedder_type=query_embedder_type
        )
        
        # Layer 4: Vector Database
        self.vector_store = HealthcareVectorStore(
            url=qdrant_url,
            vector_size=self.embedder.local_dimension
        )
        
        # Layer 5: Hybrid Retrieval
        self.two_step_retriever = TwoStepRetrieval(
            embedder=self.embedder,
            vector_store=self.vector_store
        )
        
        self.bm25_search = BM25Search(url=elasticsearch_url)
        self.hybrid_retriever = HealthcareHybridRetriever(
            two_step_retriever=self.two_step_retriever,
            bm25_search=self.bm25_search
        )
        
        # Layer 6: Generation
        self.generator = HealthcareRAGGenerator(
            model=ollama_generation_model,
            base_url=ollama_base_url
        )
        
        # Layer 7: Semantic Cache
        self.cache = HealthcareSemanticCache(host=redis_host)
        
        logger.info("SemanticPatternOrchestrator initialized with all 7 layers")
    
    def _get_document_metadata(self, source_path: str) -> Optional[Dict[str, Any]]:
        """
        Get stored metadata for a document if it exists.

        Args:
            source_path: Source file path

        Returns:
            Document metadata dict with file_hash and file_mtime, or None if not found
        """
        try:
            # Use a small search to get metadata
            dummy_embedding = self.embedder.embed_query("test")
            results = self.vector_store.search(
                dummy_embedding,
                top_k=1,
                filters={"source_path": source_path}
            )

            if results and len(results) > 0:
                # Return the metadata from the first chunk
                return results[0].get("metadata", {})
            else:
                return None

        except Exception as e:
            logger.debug(f"Error getting document metadata: {e}")
            return None

    def _document_exists(self, source_path: str) -> bool:
        """
        Check if a document already exists in the system.

        Args:
            source_path: Source file path

        Returns:
            True if document exists, False otherwise
        """
        return self._get_document_metadata(source_path) is not None

    def _has_document_changed(
        self,
        file_path: str,
        stored_metadata: Dict[str, Any]
    ) -> bool:
        """
        Check if document has changed since last ingestion.

        Compares file hash and modification time.

        Args:
            file_path: Current file path
            stored_metadata: Metadata from previously ingested document

        Returns:
            True if document has changed, False otherwise
        """
        # Get current file hash and mtime
        current_hash = self._get_file_hash(file_path)
        current_mtime = self._get_file_mtime(file_path)

        # Get stored hash and mtime
        stored_hash = stored_metadata.get("file_hash", "")
        stored_mtime = stored_metadata.get("file_mtime", 0.0)

        # Compare hash first (most reliable)
        if current_hash and stored_hash:
            if current_hash != stored_hash:
                logger.info(
                    f"Document hash changed: {file_path}\n"
                    f"  Stored:  {stored_hash[:16]}...\n"
                    f"  Current: {current_hash[:16]}..."
                )
                return True
            else:
                logger.debug(f"Document hash unchanged: {file_path}")
                return False

        # Fall back to mtime if hash not available
        if current_mtime > stored_mtime:
            logger.info(
                f"Document mtime changed: {file_path}\n"
                f"  Stored:  {stored_mtime}\n"
                f"  Current: {current_mtime}"
            )
            return True

        logger.debug(f"Document unchanged: {file_path}")
        return False
    
    def _get_file_hash(self, file_path: str) -> str:
        """
        Get file hash for change detection.
        
        Args:
            file_path: Path to file
            
        Returns:
            SHA256 hash of file content
        """
        try:
            with open(file_path, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
            return file_hash
        except Exception as e:
            logger.warning(f"Error computing file hash for {file_path}: {e}")
            return ""
    
    def _get_file_mtime(self, file_path: str) -> float:
        """
        Get file modification time.
        
        Args:
            file_path: Path to file
            
        Returns:
            Modification time as float
        """
        try:
            return os.path.getmtime(file_path)
        except Exception as e:
            logger.warning(f"Error getting mtime for {file_path}: {e}")
            return 0.0
    
    def ingest_document(
        self,
        document_path: str,
        metadata: Optional[Dict[str, Any]] = None,
        force_reingest: bool = False
    ) -> int:
        """
        Ingest a single document through the pipeline.
        
        Checks if document exists and deletes old version if updated.
        
        Args:
            document_path: Path to document
            metadata: Optional metadata
            force_reingest: Force re-ingestion even if document exists
            
        Returns:
            Number of chunks created
        """
        file_path = Path(document_path)
        if not file_path.exists():
            logger.error(f"Document not found: {document_path}")
            return 0
        
        # Normalize source path (use absolute path for consistency)
        source_path = str(file_path.resolve())
        document_id = str(file_path.stem)

        # Get stored metadata if document exists
        stored_metadata = self._get_document_metadata(source_path)
        document_exists = stored_metadata is not None

        # INCREMENTAL LOGIC: Check if document has changed
        if document_exists and not force_reingest:
            # Check if document has changed using hash/mtime comparison
            has_changed = self._has_document_changed(str(file_path), stored_metadata)

            if not has_changed:
                # Document unchanged - SKIP re-ingestion
                logger.info(f"⏭️  Skipping unchanged document: {source_path}")
                return 0  # Return 0 chunks (nothing changed)
            else:
                # Document changed - delete old version and re-ingest
                logger.info(f"🔄 Re-ingesting changed document: {source_path}")
                force_reingest = True
        elif document_exists and force_reingest:
            logger.info(f"🔄 Force re-ingesting document: {source_path}")
        else:
            logger.info(f"📝 Ingesting new document: {source_path}")

        # Delete existing chunks if re-ingesting
        if force_reingest and document_exists:
            logger.info(f"Deleting existing chunks for {source_path}")
            qdrant_deleted = self.vector_store.delete_by_source_path(source_path)
            es_deleted = self.bm25_search.delete_by_source_path(source_path)
            logger.info(f"Deleted {qdrant_deleted} Qdrant points and {es_deleted} Elasticsearch documents")
        
        # Layer 1: Extract
        extraction_result = self.extractor.extract(
            document_path,
            metadata=metadata
        )
        
        # Prepare metadata
        doc_metadata = {
            **(metadata or {}),
            **extraction_result.metadata,
            "document_id": document_id,
            "source_path": source_path,
            "file_hash": self._get_file_hash(document_path),
            "file_mtime": self._get_file_mtime(document_path)
        }
        
        # Layer 2: Chunk
        chunks = self.chunker.chunk_document(
            extraction_result.text,
            doc_metadata,
            doc_type=extraction_result.metadata.get("document_type")
        )
        
        if not chunks:
            logger.warning(f"No chunks created for {document_path}")
            return 0
        
        # Layer 3: Embed
        chunk_texts = [chunk.text for chunk in chunks]
        embeddings = self.embedder.embed_documents(chunk_texts)
        
        # Layer 4: Store in Qdrant
        self.vector_store.upsert_documents(chunks, embeddings)
        
        # Also index in Elasticsearch for BM25
        es_docs = [
            {
                "id": chunk.metadata.get("chunk_id"),  # Use consistent chunk_id
                "text": chunk.text,
                "metadata": chunk.metadata
            }
            for chunk in chunks
        ]
        self.bm25_search.index_documents(es_docs)
        
        action = "Re-ingested" if document_exists else "Ingested"
        logger.info(
            f"{action} {document_path}: {len(chunks)} chunks"
        )
        
        return len(chunks)
    
    def query(
        self,
        query: str,
        top_k: int = 10,
        use_cache: bool = True,
        user_context: Optional[Dict[str, Any]] = None,
        query_embedder_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Query the RAG system.
        
        Args:
            query: User query
            top_k: Number of results
            use_cache: Whether to use semantic cache
            user_context: Optional user context
            query_embedder_type: Premium embedder to use ("ollama" or "gemini")
                If None, uses the default embedder configured at initialization
            
        Returns:
            Dictionary with answer, sources, and metadata
        """
        user_context = user_context or {}

        # Layer 7: Check cache
        if use_cache:
            # Embed query with specified or default embedder type
            query_embedding = self.embedder.embed_query(query, embedder_type=query_embedder_type)
            cached_result = self.cache.get(
                query,
                query_embedding,
                user_context
            )

            if cached_result:
                logger.info("Cache hit - returning cached result")
                return {
                    **cached_result,
                    "cache_hit": True
                }

        # Layer 5: Hybrid Retrieval
        # Pass embedder_type parameter through retrieval chain
        retrieved_docs = self.hybrid_retriever.retrieve(
            query,
            top_k=top_k,
            embedder_type=query_embedder_type
        )
        
        if not retrieved_docs:
            return {
                "answer": "I couldn't find any relevant information in the pattern library.",
                "sources": [],
                "cache_hit": False,
                "retrieved_docs": 0
            }
        
        # Layer 6: Generate Response
        result = self.generator.generate(
            query,
            retrieved_docs,
            user_context
        )
        
        # Layer 7: Cache result
        if use_cache:
            query_embedding = self.embedder.embed_query(query, embedder_type=query_embedder_type)
            self.cache.set(
                query,
                query_embedding,
                result,
                user_context
            )
        
        return {
            **result,
            "cache_hit": False,
            "retrieved_docs": len(retrieved_docs)
        }
    
    def ingest_directory(
        self,
        directory_path: str,
        pattern: str = "**/*.md"
    ) -> Dict[str, Any]:
        """
        Ingest all documents from a directory with incremental updates.

        Args:
            directory_path: Path to directory
            pattern: File pattern to match

        Returns:
            Dictionary with ingestion statistics
        """
        directory = Path(directory_path)
        if not directory.exists():
            raise ValueError(f"Directory does not exist: {directory_path}")

        files = list(directory.glob(pattern))
        logger.info(f"Found {len(files)} files to process")

        # Statistics tracking
        stats = {
            "total_files": len(files),
            "new_files": 0,
            "changed_files": 0,
            "unchanged_files": 0,
            "error_files": 0,
            "total_chunks": 0
        }

        for file_path in files:
            try:
                # Check if file exists and has changed
                source_path = str(file_path.resolve())
                stored_metadata = self._get_document_metadata(source_path)

                if stored_metadata is None:
                    # New file
                    stats["new_files"] += 1
                    status = "NEW"
                elif self._has_document_changed(str(file_path), stored_metadata):
                    # Changed file
                    stats["changed_files"] += 1
                    status = "CHANGED"
                else:
                    # Unchanged file - will be skipped
                    stats["unchanged_files"] += 1
                    status = "UNCHANGED"

                # Ingest (will skip if unchanged)
                chunks = self.ingest_document(str(file_path))
                stats["total_chunks"] += chunks

                if chunks > 0:
                    logger.info(f"  [{status}] {file_path.name}: {chunks} chunks")

            except Exception as e:
                stats["error_files"] += 1
                logger.error(f"Error ingesting {file_path}: {e}")
                continue

        # Summary
        logger.info(
            f"\n📊 Ingestion Summary:\n"
            f"  Total files:     {stats['total_files']}\n"
            f"  New files:       {stats['new_files']}\n"
            f"  Changed files:   {stats['changed_files']}\n"
            f"  Unchanged files: {stats['unchanged_files']}\n"
            f"  Errors:          {stats['error_files']}\n"
            f"  Total chunks:    {stats['total_chunks']}"
        )

        return stats
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get system statistics.
        
        Returns:
            Dictionary with system stats
        """
        qdrant_info = self.vector_store.get_collection_info()
        
        return {
            "qdrant": qdrant_info,
            "embedding_models": {
                "local": "all-MiniLM-L12-v2",
                "qwen": "qwen3:14b"
            },
            "vector_dimension": self.embedder.local_dimension
        }

