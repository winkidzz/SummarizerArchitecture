"""
Main Orchestrator

Wires all 7 layers together into a complete RAG pipeline.
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import logging
import os
import hashlib
import time

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
from .monitoring import QueryTelemetry, MetricsCollector
from .web.providers import DuckDuckGoProvider, TrafilaturaProvider, WebSearchConfig
from .web.knowledge_base import WebKnowledgeBaseManager, WebKnowledgeBaseConfig

logger = logging.getLogger(__name__)
metrics = MetricsCollector()


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
        ollama_base_url: str = "http://localhost:11434",
        # Web search configuration (Phase 1)
        enable_web_search: bool = False,
        web_search_provider_type: str = "duckduckgo"
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
            enable_web_search: Enable web search integration (default: False)
            web_search_provider_type: Web search provider ("duckduckgo")
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
        ollama_keep_alive = os.getenv("OLLAMA_KEEP_ALIVE", "10m")
        logger.info(f"Initializing HybridEmbedder with default embedder type: {query_embedder_type}")

        self.embedder = HealthcareHybridEmbedder(
            local_model_name="all-MiniLM-L12-v2",
            qwen_model=ollama_model,
            ollama_base_url=ollama_base_url,
            ollama_keep_alive=ollama_keep_alive,
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

        # Web search provider (optional, Phase 1)
        # Trafilatura is PRIMARY, DuckDuckGo is fallback
        self.web_search_provider = None
        if enable_web_search:
            web_config = WebSearchConfig(
                default_provider=web_search_provider_type,
                # Trafilatura settings
                trafilatura_timeout=int(os.getenv("WEB_SEARCH_TRAFILATURA_TIMEOUT", "10")),
                trafilatura_favor_recall=os.getenv("WEB_SEARCH_TRAFILATURA_FAVOR_RECALL", "true").lower() == "true",
                # DuckDuckGo settings
                ddg_max_results=int(os.getenv("WEB_SEARCH_MAX_RESULTS", "5")),
                ddg_region=os.getenv("WEB_SEARCH_REGION", "wt-wt"),
                ddg_safesearch=os.getenv("WEB_SEARCH_SAFESEARCH", "moderate"),
                # Trust scoring
                enable_trust_scoring=os.getenv("WEB_SEARCH_TRUST_SCORING", "true").lower() == "true",
                trusted_domains=os.getenv("WEB_SEARCH_TRUSTED_DOMAINS", ".gov,.edu,.org").split(","),
                max_queries_per_minute=int(os.getenv("WEB_SEARCH_MAX_QUERIES_PER_MINUTE", "10")),
                # Hybrid mode
                trafilatura_fallback_to_ddg=True,
                use_trafilatura_with_ddg_urls=True
            )

            if web_search_provider_type in ["trafilatura", "hybrid"]:
                try:
                    # Initialize DuckDuckGo as fallback
                    ddg_provider = DuckDuckGoProvider(config=web_config)
                    # Initialize Trafilatura with DuckDuckGo fallback
                    self.web_search_provider = TrafilaturaProvider(
                        config=web_config,
                        ddg_fallback=ddg_provider
                    )
                    logger.info("Web search enabled with Trafilatura (primary) + DuckDuckGo (fallback)")
                except Exception as e:
                    logger.warning(f"Could not initialize Trafilatura, falling back to DuckDuckGo only: {e}")
                    try:
                        self.web_search_provider = DuckDuckGoProvider(config=web_config)
                        logger.info("Web search enabled with DuckDuckGo provider only")
                    except Exception as e2:
                        logger.warning(f"Could not initialize DuckDuckGo either: {e2}")
                        logger.warning("Web search will be disabled")
            elif web_search_provider_type == "duckduckgo":
                try:
                    self.web_search_provider = DuckDuckGoProvider(config=web_config)
                    logger.info("Web search enabled with DuckDuckGo provider only")
                except Exception as e:
                    logger.warning(f"Could not initialize web search: {e}")
                    logger.warning("Web search will be disabled")
            else:
                logger.warning(f"Unknown web search provider: {web_search_provider_type}")

        # Web Knowledge Base (Phase 2 - Tier 2)
        self.web_kb_manager = None
        enable_web_kb = os.getenv("ENABLE_WEB_KNOWLEDGE_BASE", "true").lower() == "true"
        if enable_web_search and enable_web_kb:
            try:
                web_kb_config = WebKnowledgeBaseConfig(
                    qdrant_url=qdrant_url or os.getenv("QDRANT_URL", "http://localhost:6333"),
                    collection_name=os.getenv("WEB_KB_COLLECTION_NAME", "web_knowledge"),
                    vector_size=self.embedder.local_dimension,
                    ttl_days=int(os.getenv("WEB_KB_TTL_DAYS", "30")),
                    max_documents=int(os.getenv("WEB_KB_MAX_SIZE", "10000")),
                    enable_auto_ingest=os.getenv("WEB_KB_ENABLE_AUTO_INGEST", "true").lower() == "true",
                    tier_weight=float(os.getenv("TIER_WEB_KB_WEIGHT", "0.9"))
                )
                self.web_kb_manager = WebKnowledgeBaseManager(
                    config=web_kb_config,
                    embedder=self.embedder
                )
                logger.info("Web Knowledge Base (Tier 2) initialized")
            except Exception as e:
                logger.warning(f"Could not initialize Web Knowledge Base: {e}")
                logger.warning("Web KB will be disabled, only live web search available")

        self.hybrid_retriever = HealthcareHybridRetriever(
            two_step_retriever=self.two_step_retriever,
            bm25_search=self.bm25_search,
            web_search_provider=self.web_search_provider,
            web_kb_manager=self.web_kb_manager
        )
        
        # Layer 6: Generation
        self.ollama_generation_model = ollama_generation_model  # Store for later use
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
        query_embedder_type: Optional[str] = None,
        telemetry: Optional[QueryTelemetry] = None,
        # Web search parameters (Phase 1)
        enable_web_search: bool = False,
        web_mode: str = "on_low_confidence"
    ) -> Dict[str, Any]:
        """
        Query the RAG system with optional web search.

        Args:
            query: User query
            top_k: Number of results
            use_cache: Whether to use semantic cache
            user_context: Optional user context
            query_embedder_type: Premium embedder to use ("ollama" or "gemini")
                If None, uses the default embedder configured at initialization
            telemetry: Optional telemetry object for tracking
            enable_web_search: Enable live web search (default: False)
            web_mode: Web search mode - "parallel" or "on_low_confidence"

        Returns:
            Dictionary with answer, sources, and metadata
        """
        user_context = user_context or {}

        # Layer 7: Check cache
        if use_cache:
            cache_start = time.time()
            # Embed query with specified or default embedder type
            embed_start = time.time()
            query_embedding = self.embedder.embed_query(query, embedder_type=query_embedder_type)
            embed_duration = time.time() - embed_start
            
            # Record embedding metrics
            if telemetry:
                telemetry.record_embedding(
                    embedder_type=query_embedder_type or "default",
                    duration=embed_duration
                )
            
            cached_result = self.cache.get(
                query,
                query_embedding,
                user_context
            )
            cache_duration = time.time() - cache_start
            
            # Record cache metrics
            if telemetry:
                telemetry.record_cache(hit=bool(cached_result))
                telemetry.record_stage("cache_check", cache_duration)
            metrics.record_cache("semantic", "get", hit=bool(cached_result))

            if cached_result:
                logger.info("Cache hit - returning cached result")
                return {
                    **cached_result,
                    "cache_hit": True
                }

        # Layer 5: Hybrid Retrieval
        retrieval_start = time.time()
        # Pass embedder_type and web search parameters through retrieval chain
        retrieved_docs = self.hybrid_retriever.retrieve(
            query,
            top_k=top_k,
            embedder_type=query_embedder_type,
            enable_web_search=enable_web_search,
            web_mode=web_mode
        )
        retrieval_duration = time.time() - retrieval_start
        
        # Calculate average similarity score if available
        avg_score = None
        if retrieved_docs and hasattr(retrieved_docs[0], 'get'):
            scores = [doc.get('score', 0) for doc in retrieved_docs if isinstance(doc, dict)]
            if scores:
                avg_score = sum(scores) / len(scores)
        
        # Record retrieval metrics
        if telemetry:
            telemetry.record_retrieval(
                retriever_type="hybrid",
                stage="final",
                duration=retrieval_duration,
                doc_count=len(retrieved_docs) if retrieved_docs else 0,
                avg_score=avg_score
            )
        
        if not retrieved_docs:
            return {
                "answer": "I couldn't find any relevant information in the pattern library.",
                "sources": [],
                "cache_hit": False,
                "retrieved_docs": 0,
                "citations": [],
                "retrieval_stats": {
                    "tier_1_results": 0,
                    "tier_2_results": 0,
                    "tier_3_results": 0
                }
            }

        # Phase 2: Extract citations and retrieval stats
        citations = []
        retrieval_stats = {
            "tier_1_results": 0,  # Pattern Library
            "tier_2_results": 0,  # Web KB
            "tier_3_results": 0,  # Live Web
            "cache_hit": False
        }

        # Collect detailed metrics for each retrieved document
        retrieval_metrics = {
            "documents": [],
            "tier_breakdown": {
                "tier_1": {"count": 0, "avg_score": 0, "max_score": 0, "documents": []},
                "tier_2": {"count": 0, "avg_score": 0, "max_score": 0, "documents": []},
                "tier_3": {"count": 0, "avg_score": 0, "max_score": 0, "documents": []}
            },
            "decision_path": {
                "cache_checked": use_cache,
                "cache_hit": False,
                "vector_search_used": True,
                "bm25_search_used": True,
                "web_kb_used": enable_web_search,
                "web_live_used": enable_web_search,
                "rrf_fusion_used": True,
                "reranking_used": True
            },
            "search_parameters": {
                "query": query,
                "top_k": top_k,
                "embedder_type": query_embedder_type or "default",
                "enable_web_search": enable_web_search,
                "web_mode": web_mode if enable_web_search else None
            }
        }

        citation_id = 1
        for rank, doc in enumerate(retrieved_docs, 1):
            metadata = doc.get("metadata", {})
            # Check both 'layer' (old) and 'source_type' (new) for backwards compatibility
            source = metadata.get("source_type") or metadata.get("layer", "pattern_library")

            # Get all possible scores
            score = doc.get("score") or doc.get("similarity_score") or doc.get("rrf_score", 0.0)

            # Determine tier
            tier = "tier_1"
            tier_num = 1
            if source == "web_knowledge_base":
                retrieval_stats["tier_2_results"] += 1
                retrieval_stats["cache_hit"] = True
                tier = "tier_2"
                tier_num = 2
            elif source == "web_search":
                retrieval_stats["tier_3_results"] += 1
                tier = "tier_3"
                tier_num = 3
            else:
                retrieval_stats["tier_1_results"] += 1

            # Collect document metrics
            doc_metrics = {
                "rank": rank,
                "tier": tier_num,
                "source_type": source,
                "document_id": metadata.get("document_id", "Unknown"),
                "source_path": metadata.get("source_path", "Unknown"),
                "score": score,
                "rrf_score": doc.get("rrf_score"),
                "similarity_score": doc.get("similarity_score") or doc.get("score"),
                "trust_score": metadata.get("trust_score"),
                "url": metadata.get("url"),
                "title": metadata.get("title", "Untitled"),
                "chunk_text": doc.get("text", "")[:200] + "..." if doc.get("text") else ""
            }

            # Remove None values
            doc_metrics = {k: v for k, v in doc_metrics.items() if v is not None}
            retrieval_metrics["documents"].append(doc_metrics)

            # Update tier breakdown
            retrieval_metrics["tier_breakdown"][tier]["count"] += 1
            retrieval_metrics["tier_breakdown"][tier]["documents"].append(doc_metrics)

            # Update tier scores
            tier_scores = [d["score"] for d in retrieval_metrics["tier_breakdown"][tier]["documents"] if "score" in d]
            if tier_scores:
                retrieval_metrics["tier_breakdown"][tier]["avg_score"] = sum(tier_scores) / len(tier_scores)
                retrieval_metrics["tier_breakdown"][tier]["max_score"] = max(tier_scores)

            # Extract citation if available
            citation_text = metadata.get("citation_text")
            if citation_text:
                citation = {
                    "id": citation_id,
                    "citation_apa": citation_text,
                    "source_type": source,  # Use the normalized source
                    "trust_score": metadata.get("trust_score", 1.0),
                    "url": metadata.get("url"),
                    "title": metadata.get("title"),
                    "access_date": metadata.get("fetched_timestamp") or metadata.get("access_date")
                }
                # Remove None values
                citation = {k: v for k, v in citation.items() if v is not None}
                citations.append(citation)
                citation_id += 1

        # Layer 6: Generate Response
        generation_start = time.time()
        result = self.generator.generate(
            query,
            retrieved_docs,
            user_context
        )
        generation_duration = time.time() - generation_start
        
        # Estimate token usage (rough approximation)
        # In production, get actual token counts from the LLM response
        estimated_tokens = len(result.get("answer", "").split()) * 1.3  # Rough estimate
        
        # Record generation metrics
        if telemetry:
            telemetry.record_generation(
                model_type=self.ollama_generation_model,
                duration=generation_duration,
                tokens=int(estimated_tokens)
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
            metrics.record_cache("semantic", "set", hit=None)
        
        return {
            **result,
            "cache_hit": False,
            "retrieved_docs": len(retrieved_docs),
            "citations": citations,  # Phase 2: Citations for audit/compliance
            "retrieval_stats": retrieval_stats,  # Phase 2: Tier breakdown
            "retrieval_metrics": retrieval_metrics  # Detailed metrics for UI display
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

