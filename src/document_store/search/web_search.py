"""
Web search tool for dynamically retrieving relevant content
to update the architecture pattern knowledge base.
"""

from typing import List, Dict, Any, Optional
import logging

try:
    from duckduckgo_search import DDGS
except ImportError:
    DDGS = None
    try:
        # Alternative: googlesearch-python
        from googlesearch import search as google_search
        GOOGLE_SEARCH_AVAILABLE = True
    except ImportError:
        GOOGLE_SEARCH_AVAILABLE = False

logger = logging.getLogger(__name__)


class WebSearchTool:
    """
    Web search tool for retrieving relevant content from the web.
    
    Supports multiple search backends (DuckDuckGo, Google, etc.)
    """

    def __init__(self, backend: str = "duckduckgo"):
        """
        Initialize the web search tool.
        
        Args:
            backend: Search backend to use ('duckduckgo' or 'google')
        """
        self.backend = backend
        
        if backend == "duckduckgo":
            if DDGS is None:
                raise ImportError(
                    "duckduckgo-search is not installed. "
                    "Install it with: pip install duckduckgo-search"
                )
            self.search_engine = DDGS()
        elif backend == "google":
            if not GOOGLE_SEARCH_AVAILABLE:
                raise ImportError(
                    "googlesearch-python is not installed. "
                    "Install it with: pip install googlesearch-python"
                )
            self.search_engine = None  # Google search doesn't need initialization
        else:
            raise ValueError(f"Unsupported search backend: {backend}")
        
        logger.info(f"WebSearchTool initialized with backend: {backend}")

    def search(
        self,
        query: str,
        max_results: int = 10,
        region: str = "us-en",
    ) -> List[Dict[str, Any]]:
        """
        Perform a web search and return results.
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            region: Search region (for DuckDuckGo)
            
        Returns:
            List of search result dictionaries with:
                - title: Result title
                - url: Result URL
                - snippet: Result snippet/description
                - source: Search backend used
        """
        results = []
        
        try:
            if self.backend == "duckduckgo":
                search_results = self.search_engine.text(
                    query,
                    max_results=max_results,
                    region=region,
                )
                
                for result in search_results:
                    results.append({
                        "title": result.get("title", ""),
                        "url": result.get("href", ""),
                        "snippet": result.get("body", ""),
                        "source": "duckduckgo",
                    })
            
            elif self.backend == "google":
                search_results = google_search(
                    query,
                    num_results=max_results,
                )
                
                for url in search_results:
                    results.append({
                        "title": "",  # Google search doesn't provide title in basic mode
                        "url": url,
                        "snippet": "",
                        "source": "google",
                    })
            
            logger.info(f"Search '{query}' returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Error performing web search: {str(e)}")
            return []

    def search_architecture_patterns(
        self,
        pattern_name: Optional[str] = None,
        technique: Optional[str] = None,
        vendor: Optional[str] = None,
        max_results: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Search for architecture patterns and techniques.
        
        Args:
            pattern_name: Name of pattern to search for
            technique: Technique or technology to search for
            vendor: Vendor name to search for
            max_results: Maximum number of results
            
        Returns:
            List of search results
        """
        # Build search query
        query_parts = []
        
        if pattern_name:
            query_parts.append(pattern_name)
        if technique:
            query_parts.append(technique)
        if vendor:
            query_parts.append(vendor)
        
        if not query_parts:
            query_parts.append("AI architecture patterns RAG")
        
        query = " ".join(query_parts)
        query += " summarization architecture"
        
        return self.search(query, max_results=max_results)

