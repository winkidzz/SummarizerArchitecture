"""
RAG Query Interface for querying architecture patterns
from the document store.
"""

from typing import List, Dict, Any, Optional
import logging

from ..storage.vector_store import VectorStore

logger = logging.getLogger(__name__)


class RAGQueryInterface:
    """
    Interface for RAG systems and agents to query architecture patterns.
    
    Provides methods to search the document store and retrieve relevant
    architecture pattern information.
    """

    def __init__(self, vector_store: VectorStore):
        """
        Initialize the RAG query interface.
        
        Args:
            vector_store: Initialized VectorStore instance
        """
        self.vector_store = vector_store
        logger.info("RAGQueryInterface initialized")

    def query_patterns(
        self,
        query: str,
        n_results: int = 5,
        pattern_type: Optional[str] = None,
        vendor: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Query for architecture patterns matching the query.
        
        Args:
            query: Search query text
            n_results: Number of results to return
            pattern_type: Optional filter by pattern type (e.g., 'basic-rag', 'advanced-rag')
            vendor: Optional filter by vendor (e.g., 'gemini', 'anthropic')
            
        Returns:
            Dictionary containing query results and metadata
        """
        # Build metadata filter
        filter_metadata = {}
        if pattern_type:
            filter_metadata["pattern_type"] = pattern_type
        if vendor:
            filter_metadata["vendor"] = vendor
        
        # Query vector store
        results = self.vector_store.query(
            query_text=query,
            n_results=n_results,
            filter_metadata=filter_metadata if filter_metadata else None,
        )
        
        # Format results
        formatted_results = {
            "query": query,
            "results": [
                {
                    "content": doc,
                    "metadata": meta,
                    "distance": dist,
                    "id": doc_id,
                }
                for doc, meta, dist, doc_id in zip(
                    results["documents"],
                    results["metadatas"],
                    results["distances"],
                    results["ids"],
                )
            ],
            "count": len(results["documents"]),
        }
        
        logger.info(f"Query '{query}' returned {formatted_results['count']} results")
        return formatted_results

    def get_pattern_by_id(self, pattern_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific pattern by its ID.
        
        Args:
            pattern_id: Document ID in the vector store
            
        Returns:
            Pattern document or None if not found
        """
        results = self.vector_store.query(
            query_text="",  # Empty query, will use ID
            n_results=1,
        )
        
        # Search for the ID in results
        for doc, meta, doc_id in zip(
            results["documents"],
            results["metadatas"],
            results["ids"],
        ):
            if doc_id == pattern_id:
                return {
                    "content": doc,
                    "metadata": meta,
                    "id": doc_id,
                }
        
        return None

    def list_patterns(
        self,
        pattern_type: Optional[str] = None,
        vendor: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        List all patterns matching the filters.
        
        Args:
            pattern_type: Optional filter by pattern type
            vendor: Optional filter by vendor
            
        Returns:
            List of pattern metadata dictionaries
        """
        # Use a broad query to get all patterns
        results = self.vector_store.query(
            query_text="architecture pattern",
            n_results=100,  # Get many results
        )
        
        # Filter results
        filtered_results = []
        for doc, meta, doc_id in zip(
            results["documents"],
            results["metadatas"],
            results["ids"],
        ):
            if pattern_type and meta.get("pattern_type") != pattern_type:
                continue
            if vendor and meta.get("vendor") != vendor:
                continue
            
            filtered_results.append({
                "id": doc_id,
                "metadata": meta,
                "preview": doc[:200] + "..." if len(doc) > 200 else doc,
            })
        
        return filtered_results

