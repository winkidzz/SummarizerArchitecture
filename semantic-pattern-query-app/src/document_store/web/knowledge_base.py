"""
Web Knowledge Base Manager

Manages persistent storage of web search results in Qdrant for:
- Caching: Avoid repeated fetches
- Audit Trail: Full provenance tracking
- Citations: Proper source attribution
- Continuous Learning: Usage analytics

Architecture:
    Tier 2 in 3-tier retrieval system:
    1. Pattern Library (weight 1.0)
    2. Web Knowledge Base (weight 0.9) ← This module
    3. Live Web Search (weight 0.7)
"""

import hashlib
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass, field
from uuid import uuid4

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import (
        Distance,
        VectorParams,
        PointStruct,
        Filter,
        FieldCondition,
        MatchValue,
        Range
    )
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False
    QdrantClient = None

from .providers import WebSearchResult

logger = logging.getLogger(__name__)


@dataclass
class WebKnowledgeBaseConfig:
    """Configuration for Web Knowledge Base."""

    # Qdrant settings
    qdrant_url: str = "http://localhost:6333"
    collection_name: str = "web_knowledge"
    vector_size: int = 768  # nomic-embed-text dimension

    # TTL and freshness
    ttl_days: int = 30
    refresh_threshold_days: int = 7

    # Size limits
    max_documents: int = 10000

    # Features
    enable_auto_ingest: bool = True
    enable_auto_refresh: bool = True
    enable_deduplication: bool = True

    # Tier weights (for RRF fusion)
    tier_weight: float = 0.9


@dataclass
class WebKnowledgeDocument:
    """Document stored in Web Knowledge Base."""

    id: str
    content: str
    embedding: List[float]

    # Source metadata (audit trail)
    url: str
    domain: str
    title: str
    author: Optional[str] = None
    content_date: Optional[str] = None

    # Extraction metadata
    extraction_method: str = "trafilatura"
    fetched_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    character_count: int = 0

    # Trust & quality
    trust_score: float = 0.5
    domain_type: str = "default"  # trusted | default | blocked

    # Freshness
    expiry_date: str = field(default_factory=lambda: (datetime.now() + timedelta(days=30)).isoformat())
    is_expired: bool = False

    # Usage analytics
    query_triggered_by: str = ""
    times_retrieved: int = 0
    last_retrieved: Optional[str] = None
    citation_count: int = 0

    # Citation
    citation_text: str = ""

    # Content hash for deduplication
    content_hash: str = ""


class WebKnowledgeBaseManager:
    """
    Manages Web Knowledge Base in Qdrant.

    Features:
    - Auto-ingestion of web search results
    - Deduplication by URL and content hash
    - Freshness checking and TTL
    - Usage analytics for reinforcement learning
    - Citation generation
    - Audit trail

    Example:
        config = WebKnowledgeBaseConfig()
        manager = WebKnowledgeBaseManager(config, embedder)

        # Ingest web results
        await manager.ingest_web_results(web_results, query="latest RAG")

        # Search knowledge base
        kb_results = await manager.search(query="RAG patterns", top_k=5)
    """

    def __init__(
        self,
        config: WebKnowledgeBaseConfig,
        embedder: Any = None
    ):
        """
        Initialize Web Knowledge Base Manager.

        Args:
            config: Configuration for Web KB
            embedder: Embedder instance for vectorization
        """
        if not QDRANT_AVAILABLE:
            raise ImportError(
                "qdrant-client is not installed. "
                "Install it with: pip install qdrant-client"
            )

        self.config = config
        self.embedder = embedder
        self.client = QdrantClient(url=config.qdrant_url)

        # Initialize collection
        self._ensure_collection_exists()

        logger.info(
            f"WebKnowledgeBaseManager initialized: "
            f"collection={config.collection_name}, "
            f"ttl={config.ttl_days}d, "
            f"auto_ingest={config.enable_auto_ingest}"
        )

    def _ensure_collection_exists(self):
        """Create Qdrant collection if it doesn't exist."""
        try:
            collections = self.client.get_collections().collections
            collection_names = [c.name for c in collections]

            if self.config.collection_name not in collection_names:
                logger.info(f"Creating collection: {self.config.collection_name}")

                self.client.create_collection(
                    collection_name=self.config.collection_name,
                    vectors_config=VectorParams(
                        size=self.config.vector_size,
                        distance=Distance.COSINE
                    )
                )

                logger.info(f"Collection created: {self.config.collection_name}")
            else:
                logger.info(f"Collection exists: {self.config.collection_name}")

        except Exception as e:
            logger.error(f"Error ensuring collection exists: {e}")
            raise

    def _calculate_content_hash(self, content: str) -> str:
        """Calculate SHA256 hash of content for deduplication."""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def _prepare_text_for_embedding(self, text: str, max_chars: int = 3000) -> str:
        """
        Prepare text for embedding by chunking if too large.

        Ollama can fail on very large texts (>10KB). This method intelligently
        truncates the text to fit within embedding limits by taking the beginning
        and end of the content.

        Args:
            text: The full text content to prepare
            max_chars: Maximum characters to keep (default 3000)

        Returns:
            Truncated text suitable for embedding
        """
        if len(text) <= max_chars:
            return text

        # For large text, take beginning and end (most important parts)
        chunk_size = max_chars // 2
        beginning = text[:chunk_size]
        end = text[-chunk_size:]

        # Add separator to indicate truncation
        truncated = f"{beginning}\n\n[... content truncated ...]\n\n{end}"

        logger.info(f"Truncated text from {len(text)} to {len(truncated)} chars for embedding")
        return truncated

    def _generate_citation(
        self,
        title: str,
        url: str,
        author: Optional[str] = None,
        content_date: Optional[str] = None,
        format: str = "apa"
    ) -> str:
        """
        Generate citation in specified format.

        Args:
            title: Article title
            url: Source URL
            author: Author name (optional)
            content_date: Publication date (optional)
            format: Citation format (apa, mla, chicago)

        Returns:
            Formatted citation string
        """
        if format == "apa":
            # APA format: Author (Year). Title. URL
            citation = ""
            if author:
                citation += f"{author} "
            if content_date:
                try:
                    year = datetime.fromisoformat(content_date).year
                    citation += f"({year}). "
                except:
                    citation += "(n.d.). "
            else:
                citation += "(n.d.). "
            citation += f"{title}. Retrieved from {url}"
            return citation

        # Default to simple format
        return f"{title} - {url}"

    def check_exists(self, url: str) -> Optional[WebKnowledgeDocument]:
        """
        Check if URL already exists in knowledge base.

        Args:
            url: URL to check

        Returns:
            Existing document if found, None otherwise
        """
        try:
            # Search by URL
            results = self.client.scroll(
                collection_name=self.config.collection_name,
                scroll_filter=Filter(
                    must=[
                        FieldCondition(
                            key="url",
                            match=MatchValue(value=url)
                        )
                    ]
                ),
                limit=1
            )

            if results[0]:  # results is tuple (points, next_offset)
                point = results[0][0]
                return self._point_to_document(point)

            return None

        except Exception as e:
            logger.error(f"Error checking if URL exists: {e}")
            return None

    def ingest_web_result(
        self,
        result: WebSearchResult,
        query: str = "",
        embedding: Optional[List[float]] = None
    ) -> Optional[str]:
        """
        Ingest single web search result into knowledge base.

        Args:
            result: Web search result to ingest
            query: Original query that triggered this result
            embedding: Pre-computed embedding (optional)

        Returns:
            Document ID if ingested, None if skipped
        """
        try:
            # Check if URL already exists
            existing = self.check_exists(result.url)

            if existing:
                # Update access metadata
                self._update_access_metadata(existing.id)
                logger.info(f"URL already exists, updated access: {result.url}")
                return existing.id

            # Get full text from metadata
            full_text = result.metadata.get("full_text", result.snippet)
            if not full_text or len(full_text) < 50:
                logger.warning(f"Content too short, skipping: {result.url}")
                return None

            # Generate embedding if not provided
            if embedding is None:
                if self.embedder is None:
                    logger.error("No embedder provided, cannot generate embedding")
                    return None
                # Prepare text for embedding (chunk if too large for Ollama)
                text_for_embedding = self._prepare_text_for_embedding(full_text, max_chars=3000)

                # Retry with fallback to Gemini if Ollama fails
                max_retries = 2
                for attempt in range(max_retries):
                    try:
                        # Try Ollama first
                        if hasattr(self.embedder, 'embed_query'):
                            embedding = self.embedder.embed_query(text_for_embedding)
                            break
                    except Exception as e:
                        logger.warning(f"Embedding attempt {attempt + 1}/{max_retries} failed: {e}")
                        if attempt == max_retries - 1:
                            # Last attempt: try Gemini fallback
                            try:
                                logger.info("Falling back to Gemini embedder for large content")
                                embedding = self.embedder.embed_query(text_for_embedding, embedder_type='gemini')
                                break
                            except Exception as gemini_error:
                                logger.error(f"Gemini fallback also failed: {gemini_error}")
                                return None
                        import time
                        time.sleep(0.5 * (attempt + 1))  # Exponential backoff

            # Calculate content hash
            content_hash = self._calculate_content_hash(full_text)

            # Check for duplicate content by hash
            if self.config.enable_deduplication:
                duplicate = self._check_content_duplicate(content_hash)
                if duplicate:
                    logger.info(f"Duplicate content found, skipping: {result.url}")
                    return None

            # Create document
            doc_id = str(uuid4())
            citation = self._generate_citation(
                title=result.title,
                url=result.url,
                author=result.metadata.get("author"),
                content_date=result.metadata.get("date")
            )

            expiry_date = datetime.now() + timedelta(days=self.config.ttl_days)

            # Create Qdrant point
            point = PointStruct(
                id=doc_id,
                vector=embedding,
                payload={
                    "content": full_text,
                    "content_hash": content_hash,

                    # Source metadata
                    "url": result.url,
                    "domain": result.domain,
                    "title": result.title,
                    "author": result.metadata.get("author"),
                    "content_date": result.metadata.get("date"),

                    # Extraction metadata
                    "extraction_method": result.metadata.get("extraction_method", "trafilatura"),
                    "fetched_timestamp": datetime.now().isoformat(),
                    "character_count": len(full_text),

                    # Trust & quality
                    "trust_score": result.trust_score,
                    "domain_type": self._classify_domain(result.domain),

                    # Freshness
                    "expiry_date": expiry_date.isoformat(),
                    "is_expired": False,
                    "refresh_count": 0,

                    # Usage analytics
                    "query_triggered_by": query,
                    "times_retrieved": 0,
                    "last_retrieved": None,
                    "citation_count": 0,

                    # Citation
                    "citation_text": citation,

                    # Audit trail
                    "audit_trail": [
                        {
                            "action": "created",
                            "timestamp": datetime.now().isoformat(),
                            "query": query
                        }
                    ]
                }
            )

            # Upsert to Qdrant
            self.client.upsert(
                collection_name=self.config.collection_name,
                points=[point]
            )

            logger.info(f"Ingested web result: {result.url} (id={doc_id})")
            return doc_id

        except Exception as e:
            logger.error(f"Error ingesting web result: {e}")
            return None

    def ingest_web_results(
        self,
        results: List[WebSearchResult],
        query: str = ""
    ) -> int:
        """
        Ingest multiple web search results.

        Args:
            results: List of web search results
            query: Original query

        Returns:
            Number of documents ingested
        """
        count = 0
        for result in results:
            doc_id = self.ingest_web_result(result, query)
            if doc_id:
                count += 1

        logger.info(f"Ingested {count}/{len(results)} web results for query: {query}")
        return count

    def search(
        self,
        query: str,
        top_k: int = 5,
        filter_expired: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Search web knowledge base.

        Args:
            query: Search query
            top_k: Number of results to return
            filter_expired: Filter out expired documents

        Returns:
            List of search results with metadata
        """
        try:
            if self.embedder is None:
                logger.error("No embedder provided for search")
                return []

            # Generate query embedding
            query_embedding = self.embedder.embed_query(query)

            # Build filter
            search_filter = None
            if filter_expired:
                search_filter = Filter(
                    must=[
                        FieldCondition(
                            key="is_expired",
                            match=MatchValue(value=False)
                        )
                    ]
                )

            # Search Qdrant
            from qdrant_client.models import QueryRequest

            search_results = self.client.query_points(
                collection_name=self.config.collection_name,
                query=query_embedding,
                limit=top_k,
                query_filter=search_filter
            ).points

            # Convert to result format
            results = []
            for hit in search_results:
                # Update access metadata
                self._update_access_metadata(hit.id)

                results.append({
                    "id": hit.id,
                    "score": hit.score,
                    "content": hit.payload.get("content", ""),
                    "metadata": {
                        "url": hit.payload.get("url"),
                        "title": hit.payload.get("title"),
                        "domain": hit.payload.get("domain"),
                        "author": hit.payload.get("author"),
                        "content_date": hit.payload.get("content_date"),
                        "fetched_timestamp": hit.payload.get("fetched_timestamp"),
                        "trust_score": hit.payload.get("trust_score"),
                        "citation_text": hit.payload.get("citation_text"),
                        "times_retrieved": hit.payload.get("times_retrieved", 0),
                        "layer": "web_knowledge_base",  # For tier tracking
                        "extraction_method": hit.payload.get("extraction_method")
                    }
                })

            logger.info(f"Web KB search returned {len(results)} results for: {query}")
            return results

        except Exception as e:
            logger.error(f"Error searching web knowledge base: {e}")
            return []

    def _update_access_metadata(self, doc_id: str):
        """Update access count and timestamp for a document."""
        try:
            # Get current document
            result = self.client.retrieve(
                collection_name=self.config.collection_name,
                ids=[doc_id]
            )

            if not result:
                return

            point = result[0]

            # Update metadata
            times_retrieved = point.payload.get("times_retrieved", 0) + 1

            # Update point
            self.client.set_payload(
                collection_name=self.config.collection_name,
                payload={
                    "times_retrieved": times_retrieved,
                    "last_retrieved": datetime.now().isoformat()
                },
                points=[doc_id]
            )

        except Exception as e:
            logger.error(f"Error updating access metadata: {e}")

    def _check_content_duplicate(self, content_hash: str) -> bool:
        """Check if content with same hash already exists."""
        try:
            results = self.client.scroll(
                collection_name=self.config.collection_name,
                scroll_filter=Filter(
                    must=[
                        FieldCondition(
                            key="content_hash",
                            match=MatchValue(value=content_hash)
                        )
                    ]
                ),
                limit=1
            )

            return len(results[0]) > 0

        except Exception as e:
            logger.error(f"Error checking content duplicate: {e}")
            return False

    def _classify_domain(self, domain: str) -> str:
        """Classify domain type for trust scoring."""
        domain_lower = domain.lower()

        if any(domain_lower.endswith(tld) for tld in [".gov", ".edu", ".org"]):
            return "trusted"

        # Add more classification logic as needed
        return "default"

    def _point_to_document(self, point: Any) -> WebKnowledgeDocument:
        """Convert Qdrant point to WebKnowledgeDocument."""
        return WebKnowledgeDocument(
            id=point.id,
            content=point.payload.get("content", ""),
            embedding=point.vector if hasattr(point, 'vector') else [],
            url=point.payload.get("url", ""),
            domain=point.payload.get("domain", ""),
            title=point.payload.get("title", ""),
            author=point.payload.get("author"),
            content_date=point.payload.get("content_date"),
            extraction_method=point.payload.get("extraction_method", "trafilatura"),
            fetched_timestamp=point.payload.get("fetched_timestamp", ""),
            character_count=point.payload.get("character_count", 0),
            trust_score=point.payload.get("trust_score", 0.5),
            domain_type=point.payload.get("domain_type", "default"),
            expiry_date=point.payload.get("expiry_date", ""),
            is_expired=point.payload.get("is_expired", False),
            query_triggered_by=point.payload.get("query_triggered_by", ""),
            times_retrieved=point.payload.get("times_retrieved", 0),
            last_retrieved=point.payload.get("last_retrieved"),
            citation_count=point.payload.get("citation_count", 0),
            citation_text=point.payload.get("citation_text", ""),
            content_hash=point.payload.get("content_hash", "")
        )

    def cleanup_expired(self) -> int:
        """
        Remove expired documents from knowledge base.

        Returns:
            Number of documents removed
        """
        try:
            # Mark expired documents
            now = datetime.now().isoformat()

            # Scroll through all documents
            scroll_result = self.client.scroll(
                collection_name=self.config.collection_name,
                limit=100
            )

            expired_ids = []
            for point in scroll_result[0]:
                expiry_date = point.payload.get("expiry_date")
                if expiry_date and expiry_date < now:
                    expired_ids.append(point.id)

            # Delete expired documents
            if expired_ids:
                self.client.delete(
                    collection_name=self.config.collection_name,
                    points_selector=expired_ids
                )

                logger.info(f"Cleaned up {len(expired_ids)} expired documents")

            return len(expired_ids)

        except Exception as e:
            logger.error(f"Error cleaning up expired documents: {e}")
            return 0

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the knowledge base.

        Returns:
            Dictionary with stats
        """
        try:
            collection_info = self.client.get_collection(self.config.collection_name)

            return {
                "total_documents": collection_info.points_count,
                "collection_name": self.config.collection_name,
                "vector_size": self.config.vector_size,
                "ttl_days": self.config.ttl_days
            }

        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}
