"""
Web Search Provider Interfaces and Implementations

Protocol-based design matching the embedder architecture pattern.
Multiple providers can be loaded simultaneously and selected at runtime.

Example usage:
    config = WebSearchConfig(ddg_max_results=5)
    provider = DuckDuckGoProvider(config=config)
    results = provider.search("RAG architecture", max_results=10)
"""

from typing import Protocol, List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
from dataclasses import dataclass, field
import logging
from datetime import datetime
from urllib.parse import urlparse
import time

try:
    from ddgs import DDGS
    DDGS_AVAILABLE = True
except ImportError:
    # Try old package name for backwards compatibility
    try:
        from duckduckgo_search import DDGS
        DDGS_AVAILABLE = True
    except ImportError:
        DDGS_AVAILABLE = False
        DDGS = None

try:
    from trafilatura import fetch_url, extract
    from trafilatura.settings import use_config
    TRAFILATURA_AVAILABLE = True
except ImportError:
    TRAFILATURA_AVAILABLE = False
    fetch_url = None
    extract = None
    use_config = None

logger = logging.getLogger(__name__)


@dataclass
class WebSearchConfig:
    """
    Configuration for web search providers.

    Matches the configuration pattern used in the system for embedders and other services.
    """

    # Default provider type - Trafilatura is primary, DuckDuckGo is fallback
    default_provider: Literal["trafilatura", "duckduckgo", "hybrid"] = "hybrid"

    # Trafilatura settings (primary)
    trafilatura_timeout: int = 10  # seconds
    trafilatura_include_comments: bool = False
    trafilatura_include_tables: bool = True
    trafilatura_max_tree_size: int = 50000  # characters
    trafilatura_favor_recall: bool = True  # Prioritize completeness

    # DuckDuckGo settings (fallback)
    ddg_region: str = "wt-wt"  # worldwide
    ddg_safesearch: str = "moderate"  # off, moderate, strict
    ddg_max_results: int = 5
    ddg_timeout: int = 10  # seconds

    # Trust scoring settings
    enable_trust_scoring: bool = True
    trusted_domains: List[str] = field(default_factory=lambda: [".gov", ".edu", ".org"])
    blocked_domains: List[str] = field(default_factory=list)

    # Rate limiting
    enable_rate_limiting: bool = True
    max_queries_per_minute: int = 10

    # Hybrid mode settings
    trafilatura_fallback_to_ddg: bool = True  # If Trafilatura fails, use DuckDuckGo
    use_trafilatura_with_ddg_urls: bool = True  # Extract full content from DDG URLs


class WebSearchResult(BaseModel):
    """
    Web search result model.

    Consistent with the document retrieval format used in hybrid_retriever.
    This allows web results to be seamlessly integrated with vector and BM25 results.
    """
    rank: int = Field(..., description="Result rank in SERP (1-indexed)")
    title: str = Field(..., description="Page title")
    snippet: str = Field(..., description="Text snippet from page")
    url: str = Field(..., description="Source URL")
    provider: str = Field(..., description="Search provider name (e.g., 'duckduckgo')")

    # Optional fields for quality assessment
    trust_score: Optional[float] = Field(
        default=0.5,
        description="Trust score (0-1) based on domain reputation"
    )
    domain: Optional[str] = Field(
        default=None,
        description="Extracted domain name"
    )
    retrieved_at: Optional[datetime] = Field(
        default_factory=datetime.utcnow,
        description="When the result was retrieved"
    )

    # Metadata for tracking
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "rank": 1,
                "title": "RAG Architecture Best Practices",
                "snippet": "This article discusses best practices for RAG...",
                "url": "https://example.edu/rag-practices",
                "provider": "duckduckgo",
                "trust_score": 0.9,
                "domain": "example.edu"
            }
        }


class WebSearchProvider(Protocol):
    """
    Protocol for web search providers.

    Matches the pattern used for embedders - allows multiple implementations
    to coexist and be selected at runtime via configuration.

    Example:
        # Similar to how embedders are used
        provider = DuckDuckGoProvider(config)
        results = provider.search("query text", max_results=5)
    """

    def search(
        self,
        query: str,
        max_results: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[WebSearchResult]:
        """
        Perform web search.

        Args:
            query: Search query text
            max_results: Maximum number of results to return
            filters: Optional filters (e.g., date range, domain restrictions)

        Returns:
            List of WebSearchResult objects
        """
        ...

    def health_check(self) -> bool:
        """
        Check if provider is available and healthy.

        Returns:
            True if provider is accessible and working
        """
        ...


class DuckDuckGoProvider(WebSearchProvider):
    """
    DuckDuckGo search provider implementation.

    Uses duckduckgo-search library (free, no API key required).
    Follows the same initialization pattern as GeminiEmbedder and OllamaEmbedder.

    Features:
    - Free web search (no API key)
    - Privacy-focused
    - Domain-based trust scoring
    - Rate limiting
    - Error handling with graceful degradation

    Example:
        config = WebSearchConfig(ddg_max_results=10)
        provider = DuckDuckGoProvider(config=config)
        results = provider.search("RAG techniques 2025")
    """

    def __init__(
        self,
        config: Optional[WebSearchConfig] = None
    ):
        """
        Initialize DuckDuckGo provider.

        Args:
            config: Web search configuration (defaults if not provided)

        Raises:
            ImportError: If duckduckgo-search package is not installed
        """
        if not DDGS_AVAILABLE:
            raise ImportError(
                "duckduckgo-search package is not installed. "
                "Install it with: pip install duckduckgo-search"
            )

        self.config = config or WebSearchConfig()
        self._last_query_time = None
        self._query_count = 0

        logger.info(
            f"DuckDuckGoProvider initialized: "
            f"region={self.config.ddg_region}, "
            f"max_results={self.config.ddg_max_results}, "
            f"trust_scoring={'enabled' if self.config.enable_trust_scoring else 'disabled'}"
        )

    def search(
        self,
        query: str,
        max_results: int = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[WebSearchResult]:
        """
        Perform DuckDuckGo search.

        Args:
            query: Search query text
            max_results: Maximum results (overrides config default)
            filters: Optional filters (not yet implemented)

        Returns:
            List of WebSearchResult objects

        Note:
            Returns empty list on error (graceful degradation).
            Applies rate limiting if enabled in config.
        """
        max_results = max_results or self.config.ddg_max_results

        # Rate limiting check
        if self.config.enable_rate_limiting:
            self._check_rate_limit()

        try:
            # Perform search using DDGS
            with DDGS() as ddgs:
                raw_results = ddgs.text(
                    query,
                    region=self.config.ddg_region,
                    safesearch=self.config.ddg_safesearch,
                    max_results=max_results
                )

                # Convert to WebSearchResult objects
                search_results = []
                for rank, result in enumerate(raw_results, 1):
                    # Extract domain for trust scoring
                    domain = self._extract_domain(result.get('href', ''))

                    # Calculate trust score
                    trust_score = self._calculate_trust_score(
                        domain,
                        result.get('title', ''),
                        result.get('body', '')
                    )

                    search_result = WebSearchResult(
                        rank=rank,
                        title=result.get('title', ''),
                        snippet=result.get('body', ''),
                        url=result.get('href', ''),
                        provider="duckduckgo",
                        trust_score=trust_score,
                        domain=domain,
                        metadata={
                            "query": query,
                            "region": self.config.ddg_region,
                            "safesearch": self.config.ddg_safesearch
                        }
                    )
                    search_results.append(search_result)

                logger.info(
                    f"DuckDuckGo search returned {len(search_results)} results "
                    f"for query: {query[:50]}..."
                )
                return search_results

        except Exception as e:
            logger.error(f"DuckDuckGo search failed for query '{query}': {e}")
            return []  # Graceful degradation

    def health_check(self) -> bool:
        """
        Check if DuckDuckGo is accessible.

        Performs a simple test query to verify the service is working.

        Returns:
            True if DuckDuckGo is accessible, False otherwise
        """
        try:
            # Simple test query
            with DDGS() as ddgs:
                list(ddgs.text("test", max_results=1))
            logger.info("DuckDuckGo health check: OK")
            return True
        except Exception as e:
            logger.warning(f"DuckDuckGo health check failed: {e}")
            return False

    def _extract_domain(self, url: str) -> str:
        """
        Extract domain from URL.

        Args:
            url: Full URL

        Returns:
            Domain name (e.g., "example.com")
        """
        try:
            parsed = urlparse(url)
            return parsed.netloc
        except Exception as e:
            logger.debug(f"Failed to extract domain from {url}: {e}")
            return ""

    def _calculate_trust_score(
        self,
        domain: str,
        title: str,
        snippet: str
    ) -> float:
        """
        Calculate trust score based on domain and content.

        Simple heuristic-based scoring as per design document:
        - Trusted domains (.gov, .edu, .org): 0.9
        - Blocked domains: 0.0
        - Default: 0.5

        Future enhancements could use ML-based credibility scoring.

        Args:
            domain: Domain name
            title: Page title
            snippet: Page snippet

        Returns:
            Trust score (0.0-1.0)
        """
        if not self.config.enable_trust_scoring:
            return 0.5  # neutral score

        # Check blocked domains
        for blocked in self.config.blocked_domains:
            if blocked in domain.lower():
                logger.debug(f"Domain {domain} is blocked (score: 0.0)")
                return 0.0

        # Check trusted domains
        for trusted in self.config.trusted_domains:
            if domain.lower().endswith(trusted):
                logger.debug(f"Domain {domain} is trusted (score: 0.9)")
                return 0.9

        # Default score
        return 0.5

    def _check_rate_limit(self):
        """
        Simple rate limiting check.

        Implements a basic sliding window rate limiter.
        Sleeps if the rate limit is exceeded.
        """
        current_time = time.time()

        if self._last_query_time is None:
            self._last_query_time = current_time
            self._query_count = 1
            return

        # Reset counter every minute
        if current_time - self._last_query_time > 60:
            self._query_count = 0
            self._last_query_time = current_time

        # Check limit
        if self._query_count >= self.config.max_queries_per_minute:
            sleep_time = 60 - (current_time - self._last_query_time)
            if sleep_time > 0:
                logger.warning(
                    f"Rate limit reached ({self.config.max_queries_per_minute}/min), "
                    f"sleeping for {sleep_time:.1f}s"
                )
                time.sleep(sleep_time)
                self._query_count = 0
                self._last_query_time = time.time()

        self._query_count += 1


class TrafilaturaProvider(WebSearchProvider):
    """
    Trafilatura web content extraction provider (PRIMARY).

    Uses Trafilatura for direct web content extraction - provides cleaner,
    more complete content than search snippet APIs. Works best when you have
    specific URLs to extract from (e.g., from DuckDuckGo search results).

    Features:
    - Free web content extraction (no API key)
    - High-quality text extraction with metadata
    - Faster and more accurate than snippet-based search
    - Includes tables, lists, and structured content
    - Respects robots.txt
    - Handles malformed HTML gracefully

    Usage:
        config = WebSearchConfig(trafilatura_favor_recall=True)
        provider = TrafilaturaProvider(config=config)

        # Extract from specific URL
        results = provider.search("https://example.com/article")

        # Or provide multiple URLs
        urls = ["https://site1.com", "https://site2.com"]
        results = provider.search_urls(urls)
    """

    def __init__(
        self,
        config: Optional[WebSearchConfig] = None,
        ddg_fallback: Optional['DuckDuckGoProvider'] = None
    ):
        """
        Initialize Trafilatura provider.

        Args:
            config: Web search configuration
            ddg_fallback: Optional DuckDuckGo provider for fallback

        Raises:
            ImportError: If trafilatura package is not installed
        """
        if not TRAFILATURA_AVAILABLE:
            raise ImportError(
                "trafilatura package is not installed. "
                "Install it with: pip install trafilatura"
            )

        self.config = config or WebSearchConfig()
        self.ddg_fallback = ddg_fallback
        self._last_query_time = None
        self._query_count = 0

        # Configure Trafilatura settings
        self.trafilatura_config = use_config()
        self.trafilatura_config.set("DEFAULT", "EXTRACTION_TIMEOUT",
                                    str(self.config.trafilatura_timeout))

        logger.info(
            f"TrafilaturaProvider initialized: "
            f"timeout={self.config.trafilatura_timeout}s, "
            f"fallback_enabled={'yes' if ddg_fallback else 'no'}"
        )

    def search(
        self,
        query: str,
        max_results: int = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[WebSearchResult]:
        """
        Perform web content extraction.

        If query is a URL, extracts content directly.
        If query is search text, falls back to DuckDuckGo + Trafilatura extraction.

        Args:
            query: URL to extract from, or search query
            max_results: Maximum results (for fallback mode)
            filters: Optional filters

        Returns:
            List of WebSearchResult objects with full content

        Note:
            Returns empty list on error (graceful degradation).
            Falls back to DuckDuckGo if enabled and query is not a URL.
        """
        max_results = max_results or self.config.ddg_max_results

        # Rate limiting check
        if self.config.enable_rate_limiting:
            self._check_rate_limit()

        # Check if query is a URL
        if self._is_url(query):
            return self._extract_from_url(query, filters)

        # Not a URL - fall back to DuckDuckGo + Trafilatura extraction
        if self.config.trafilatura_fallback_to_ddg and self.ddg_fallback:
            logger.info(f"Query is not a URL, using DuckDuckGo + Trafilatura extraction")
            return self._search_with_ddg_fallback(query, max_results, filters)

        logger.warning(f"Query '{query}' is not a URL and no fallback configured")
        return []

    def search_urls(
        self,
        urls: List[str],
        filters: Optional[Dict[str, Any]] = None
    ) -> List[WebSearchResult]:
        """
        Extract content from multiple URLs.

        Args:
            urls: List of URLs to extract from
            filters: Optional filters

        Returns:
            List of WebSearchResult objects
        """
        results = []
        for rank, url in enumerate(urls, 1):
            result = self._extract_from_url(url, filters, rank=rank)
            if result:
                results.extend(result)
        return results

    def _is_url(self, text: str) -> bool:
        """Check if text is a valid URL."""
        return text.startswith(("http://", "https://"))

    def _extract_from_url(
        self,
        url: str,
        filters: Optional[Dict[str, Any]] = None,
        rank: int = 1
    ) -> List[WebSearchResult]:
        """
        Extract content from a single URL using Trafilatura.

        Args:
            url: URL to extract from
            filters: Optional filters
            rank: Result rank (for ordering)

        Returns:
            List with single WebSearchResult, or empty list on failure
        """
        try:
            logger.info(f"Extracting content from URL: {url}")

            # Fetch URL with timeout
            downloaded = fetch_url(url)
            if not downloaded:
                logger.warning(f"Failed to fetch URL: {url}")
                return []

            # Extract content with Trafilatura
            extracted_text = extract(
                downloaded,
                include_comments=self.config.trafilatura_include_comments,
                include_tables=self.config.trafilatura_include_tables,
                favor_recall=self.config.trafilatura_favor_recall,
                config=self.trafilatura_config
            )

            if not extracted_text:
                logger.warning(f"No content extracted from URL: {url}")
                return []

            # Extract metadata
            from trafilatura.metadata import extract_metadata
            metadata_obj = extract_metadata(downloaded)

            title = metadata_obj.title if metadata_obj and metadata_obj.title else url
            domain = self._extract_domain(url)

            # Calculate trust score
            trust_score = self._calculate_trust_score(domain, title, extracted_text[:500])

            # Create snippet from first 500 characters
            snippet = extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text

            result = WebSearchResult(
                rank=rank,
                title=title,
                snippet=snippet,
                url=url,
                provider="trafilatura",
                trust_score=trust_score,
                domain=domain,
                metadata={
                    "full_text": extracted_text,  # Store full extracted text
                    "author": metadata_obj.author if metadata_obj else None,
                    "date": metadata_obj.date if metadata_obj else None,
                    "extraction_method": "trafilatura"
                }
            )

            logger.info(
                f"Successfully extracted {len(extracted_text)} chars from {url} "
                f"(title: {title[:50]}...)"
            )
            return [result]

        except Exception as e:
            logger.error(f"Trafilatura extraction failed for {url}: {e}")
            return []

    def _search_with_ddg_fallback(
        self,
        query: str,
        max_results: int,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[WebSearchResult]:
        """
        Search with DuckDuckGo and extract full content with Trafilatura.

        This combines the best of both: DuckDuckGo finds relevant URLs,
        Trafilatura extracts full content (not just snippets).

        Args:
            query: Search query
            max_results: Maximum results
            filters: Optional filters

        Returns:
            List of WebSearchResult objects with full content
        """
        # Get URLs from DuckDuckGo
        ddg_results = self.ddg_fallback.search(query, max_results, filters)
        if not ddg_results:
            logger.warning(f"DuckDuckGo returned no results for query: {query}")
            return []

        logger.info(
            f"Got {len(ddg_results)} URLs from DuckDuckGo, "
            f"extracting full content with Trafilatura"
        )

        # Extract full content from each URL
        enhanced_results = []
        for ddg_result in ddg_results:
            url = ddg_result.url

            # Try to extract full content
            trafilatura_results = self._extract_from_url(
                url,
                filters,
                rank=ddg_result.rank
            )

            if trafilatura_results:
                # Use Trafilatura result (full content)
                enhanced_result = trafilatura_results[0]
                # Preserve DuckDuckGo metadata
                enhanced_result.metadata.update({
                    "ddg_snippet": ddg_result.snippet,
                    "ddg_title": ddg_result.title,
                    "extraction_method": "trafilatura+duckduckgo"
                })
                enhanced_results.append(enhanced_result)
            else:
                # Fall back to DuckDuckGo snippet
                logger.debug(f"Trafilatura extraction failed for {url}, using DDG snippet")
                ddg_result.metadata["extraction_method"] = "duckduckgo_only"
                enhanced_results.append(ddg_result)

        logger.info(
            f"Successfully enhanced {sum(1 for r in enhanced_results if 'full_text' in r.metadata)}/{len(enhanced_results)} "
            f"results with Trafilatura"
        )
        return enhanced_results

    def health_check(self) -> bool:
        """
        Check if Trafilatura is available.

        Tests extraction from a known reliable URL.

        Returns:
            True if Trafilatura is working, False otherwise
        """
        try:
            # Test with a simple URL
            test_url = "https://www.example.com"
            downloaded = fetch_url(test_url)
            if downloaded:
                extracted = extract(downloaded)
                logger.info("Trafilatura health check: OK")
                return True
            logger.warning("Trafilatura health check: Failed to fetch test URL")
            return False
        except Exception as e:
            logger.warning(f"Trafilatura health check failed: {e}")
            return False

    def _extract_domain(self, url: str) -> str:
        """
        Extract domain from URL.

        Args:
            url: Full URL

        Returns:
            Domain name (e.g., "example.com")
        """
        try:
            parsed = urlparse(url)
            return parsed.netloc
        except Exception as e:
            logger.debug(f"Failed to extract domain from {url}: {e}")
            return ""

    def _calculate_trust_score(
        self,
        domain: str,
        title: str,
        snippet: str
    ) -> float:
        """
        Calculate trust score based on domain and content.

        Simple heuristic-based scoring:
        - Trusted domains (.gov, .edu, .org): 0.9
        - Blocked domains: 0.0
        - Default: 0.5

        Args:
            domain: Domain name
            title: Page title
            snippet: Page snippet

        Returns:
            Trust score (0.0-1.0)
        """
        if not self.config.enable_trust_scoring:
            return 0.5  # neutral score

        # Check blocked domains
        for blocked in self.config.blocked_domains:
            if blocked in domain.lower():
                logger.debug(f"Domain {domain} is blocked (score: 0.0)")
                return 0.0

        # Check trusted domains
        for trusted in self.config.trusted_domains:
            if domain.lower().endswith(trusted):
                logger.debug(f"Domain {domain} is trusted (score: 0.9)")
                return 0.9

        # Default score
        return 0.5

    def _check_rate_limit(self):
        """
        Simple rate limiting check.

        Implements a basic sliding window rate limiter.
        """
        current_time = time.time()

        if self._last_query_time is None:
            self._last_query_time = current_time
            self._query_count = 1
            return

        # Reset counter every minute
        if current_time - self._last_query_time > 60:
            self._query_count = 0
            self._last_query_time = current_time

        # Check limit
        if self._query_count >= self.config.max_queries_per_minute:
            sleep_time = 60 - (current_time - self._last_query_time)
            if sleep_time > 0:
                logger.warning(
                    f"Rate limit reached ({self.config.max_queries_per_minute}/min), "
                    f"sleeping for {sleep_time:.1f}s"
                )
                time.sleep(sleep_time)
                self._query_count = 0
                self._last_query_time = time.time()

        self._query_count += 1
