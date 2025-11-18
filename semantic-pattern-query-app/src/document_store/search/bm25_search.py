"""
BM25 Search with Elasticsearch

Sparse keyword search using Elasticsearch BM25 algorithm.
Critical for exact matches and medical terminology.
"""

from typing import List, Dict, Any, Optional
import os
import logging

try:
    from elasticsearch import Elasticsearch
    ELASTICSEARCH_AVAILABLE = True
except ImportError:
    ELASTICSEARCH_AVAILABLE = False
    Elasticsearch = None

logger = logging.getLogger(__name__)


class BM25Search:
    """
    BM25 search using Elasticsearch.
    
    Provides sparse keyword search for exact matches,
    medical terminology, and structured queries.
    """
    
    def __init__(
        self,
        url: Optional[str] = None,
        index_name: str = "pattern_documents"
    ):
        """
        Initialize BM25 search.
        
        Args:
            url: Elasticsearch URL (default: from env or http://localhost:9200)
            index_name: Index name
        """
        if not ELASTICSEARCH_AVAILABLE:
            raise ImportError(
                "elasticsearch is not installed. "
                "Install it with: pip install elasticsearch"
            )
        
        self.url = url or os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")
        self.index_name = index_name
        
        # Initialize client
        # Note: Using elasticsearch<9.0.0 for ES 8.x server compatibility
        # Explicitly disable authentication for local development
        self.client = Elasticsearch(
            [self.url],
            request_timeout=30,
            verify_certs=False,  # Disable SSL verification for local
            ssl_show_warn=False
        )
        
        # Verify connection - use cluster health instead of ping
        try:
            health = self.client.cluster.health()
            if health.get('status') in ['green', 'yellow']:
                logger.debug(f"Elasticsearch cluster status: {health.get('status')}")
            else:
                logger.warning(f"Elasticsearch cluster status: {health.get('status')}")
        except Exception as e:
            raise ConnectionError(f"Could not connect to Elasticsearch at {self.url}: {e}")
        
        # Ensure index exists
        self._ensure_index()
        
        logger.info(
            f"BM25Search initialized: url={self.url}, index={self.index_name}"
        )
    
    def _ensure_index(self):
        """Create index if it doesn't exist."""
        if not self.client.indices.exists(index=self.index_name):
            logger.info(f"Creating Elasticsearch index: {self.index_name}")
            
            # Create index with mapping
            self.client.indices.create(
                index=self.index_name,
                body={
                    "mappings": {
                        "properties": {
                            "text": {
                                "type": "text",
                                "analyzer": "standard"
                            },
                            "document_id": {
                                "type": "keyword"
                            },
                            "document_type": {
                                "type": "keyword"
                            },
                            "section_type": {
                                "type": "keyword"
                            },
                            "source_path": {
                                "type": "keyword"
                            }
                        }
                    }
                }
            )
        else:
            logger.info(f"Using existing index: {self.index_name}")
    
    def index_documents(
        self,
        documents: List[Dict[str, Any]]
    ):
        """
        Index documents for BM25 search.
        
        Args:
            documents: List of document dictionaries with 'id', 'text', and 'metadata'
        """
        from elasticsearch.helpers import bulk
        
        actions = []
        for doc in documents:
            action = {
                "_index": self.index_name,
                "_id": doc.get("id"),
                "_source": {
                    "text": doc.get("text", ""),
                    **doc.get("metadata", {})
                }
            }
            actions.append(action)
        
        # Bulk index
        success, failed = bulk(self.client, actions, raise_on_error=False)
        
        if failed:
            logger.warning(f"Failed to index {len(failed)} documents")
        else:
            logger.info(f"Indexed {success} documents")
    
    def search(
        self,
        query: str,
        k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search using BM25.
        
        Args:
            query: Query text
            k: Number of results to return
            filters: Optional metadata filters
            
        Returns:
            List of result dictionaries with text, score, and metadata
        """
        # Build query
        es_query = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "match": {
                                "text": {
                                    "query": query,
                                    "operator": "or"
                                }
                            }
                        }
                    ]
                }
            },
            "size": k
        }
        
        # Add filters
        if filters:
            filter_clauses = []
            for key, value in filters.items():
                if value is not None:
                    filter_clauses.append({
                        "term": {key: value}
                    })
            
            if filter_clauses:
                es_query["query"]["bool"]["filter"] = filter_clauses
        
        # Execute search
        try:
            response = self.client.search(
                index=self.index_name,
                body=es_query
            )
        except Exception as e:
            logger.error(f"Elasticsearch search error: {e}")
            return []
        
        # Format results
        results = []
        for hit in response["hits"]["hits"]:
            source = hit["_source"]
            results.append({
                "text": source.get("text", ""),
                "score": hit["_score"],
                "metadata": {
                    k: v for k, v in source.items()
                    if k != "text"
                },
                "id": hit["_id"],
                "ranking_method": "bm25"
            })
        
        return results
    
    def delete_by_document_id(self, document_id: str) -> int:
        """
        Delete all documents for a specific document_id.
        
        Args:
            document_id: Document ID to delete
            
        Returns:
            Number of documents deleted
        """
        try:
            # Use delete_by_query to delete all documents matching document_id
            response = self.client.delete_by_query(
                index=self.index_name,
                body={
                    "query": {
                        "term": {
                            "document_id": document_id
                        }
                    }
                }
            )
            deleted_count = response.get("deleted", 0)
            logger.info(f"Deleted {deleted_count} documents for document_id: {document_id}")
            return deleted_count
        except Exception as e:
            logger.error(f"Error deleting documents for document_id {document_id}: {e}")
            return 0
    
    def delete_by_source_path(self, source_path: str) -> int:
        """
        Delete all documents for a specific source_path.
        
        Args:
            source_path: Source path to delete
            
        Returns:
            Number of documents deleted
        """
        try:
            # Use delete_by_query to delete all documents matching source_path
            response = self.client.delete_by_query(
                index=self.index_name,
                body={
                    "query": {
                        "term": {
                            "source_path": source_path
                        }
                    }
                }
            )
            deleted_count = response.get("deleted", 0)
            logger.info(f"Deleted {deleted_count} documents for source_path: {source_path}")
            return deleted_count
        except Exception as e:
            logger.error(f"Error deleting documents for source_path {source_path}: {e}")
            return 0

