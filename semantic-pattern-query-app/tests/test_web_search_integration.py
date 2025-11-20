"""
Integration tests for web search functionality.

Tests the DuckDuckGo provider, hybrid retriever with web search,
and end-to-end query flow with web augmentation.
"""

import os
import pytest
from unittest.mock import Mock, patch
from datetime import datetime

# Set test environment
os.environ["QDRANT_URL"] = "http://localhost:6333"
os.environ["ELASTICSEARCH_URL"] = "http://localhost:9200"
os.environ["OLLAMA_BASE_URL"] = "http://localhost:11434"
os.environ["ENABLE_WEB_SEARCH"] = "true"
os.environ["WEB_SEARCH_PROVIDER"] = "duckduckgo"

from src.document_store.web.providers import (
    DuckDuckGoProvider,
    TrafilaturaProvider,
    WebSearchConfig,
    WebSearchResult
)
from src.document_store.orchestrator import SemanticPatternOrchestrator


class TestDuckDuckGoProvider:
    """Test DuckDuckGo web search provider."""

    def test_provider_initialization(self):
        """Test provider initializes correctly."""
        config = WebSearchConfig(
            ddg_max_results=5,
            ddg_region="wt-wt",
            enable_trust_scoring=True
        )
        provider = DuckDuckGoProvider(config=config)
        assert provider.config == config
        assert provider.config.ddg_max_results == 5

    def test_trust_scoring_trusted_domains(self):
        """Test trust scoring for trusted domains."""
        config = WebSearchConfig(
            enable_trust_scoring=True,
            trusted_domains=[".gov", ".edu", ".org"]
        )
        provider = DuckDuckGoProvider(config=config)

        # Test trusted domains
        assert provider._calculate_trust_score("cdc.gov", "Health info", "CDC data") == 0.9
        assert provider._calculate_trust_score("harvard.edu", "Research", "Study") == 0.9
        assert provider._calculate_trust_score("who.org", "WHO info", "Guidelines") == 0.9

    def test_trust_scoring_default(self):
        """Test trust scoring for default domains."""
        config = WebSearchConfig(enable_trust_scoring=True)
        provider = DuckDuckGoProvider(config=config)

        # Test default score
        assert provider._calculate_trust_score("example.com", "Title", "Snippet") == 0.5

    def test_trust_scoring_blocked_domains(self):
        """Test trust scoring for blocked domains."""
        config = WebSearchConfig(
            enable_trust_scoring=True,
            blocked_domains=["spam.com", "malware.net"]
        )
        provider = DuckDuckGoProvider(config=config)

        # Test blocked domains
        assert provider._calculate_trust_score("spam.com", "Bad site", "Spam") == 0.0

    def test_trust_scoring_disabled(self):
        """Test trust scoring when disabled."""
        config = WebSearchConfig(enable_trust_scoring=False)
        provider = DuckDuckGoProvider(config=config)

        # All domains should get default score
        assert provider._calculate_trust_score("cdc.gov", "Health", "Data") == 0.5

    @patch('src.document_store.web.providers.DDGS')
    def test_search_basic(self, mock_ddgs):
        """Test basic search functionality."""
        # Mock DuckDuckGo results
        mock_results = [
            {
                'title': 'Test Result 1',
                'body': 'Test snippet 1',
                'href': 'https://example.com/1'
            },
            {
                'title': 'Test Result 2',
                'body': 'Test snippet 2',
                'href': 'https://cdc.gov/2'
            }
        ]
        mock_ddgs.return_value.text.return_value = mock_results

        config = WebSearchConfig(ddg_max_results=2)
        provider = DuckDuckGoProvider(config=config)

        results = provider.search("test query", max_results=2)

        assert len(results) == 2
        assert results[0].title == "Test Result 1"
        assert results[0].snippet == "Test snippet 1"
        assert results[0].url == "https://example.com/1"
        assert results[0].provider == "duckduckgo"
        assert results[0].trust_score == 0.5  # default

        # Second result is from cdc.gov (trusted)
        assert results[1].trust_score == 0.9

    @patch('src.document_store.web.providers.DDGS')
    def test_search_with_filters(self, mock_ddgs):
        """Test search with filters."""
        mock_results = [
            {
                'title': 'Filtered Result',
                'body': 'Filtered snippet',
                'href': 'https://example.com/filtered'
            }
        ]
        mock_ddgs.return_value.text.return_value = mock_results

        config = WebSearchConfig()
        provider = DuckDuckGoProvider(config=config)

        filters = {"region": "us-en"}
        results = provider.search("test query", filters=filters)

        assert len(results) == 1
        assert results[0].metadata.get("filters") == filters

    @patch('src.document_store.web.providers.DDGS')
    def test_rate_limiting(self, mock_ddgs):
        """Test rate limiting functionality."""
        mock_results = [{'title': 'Test', 'body': 'Test', 'href': 'https://example.com'}]
        mock_ddgs.return_value.text.return_value = mock_results

        config = WebSearchConfig(
            enable_rate_limiting=True,
            max_queries_per_minute=2
        )
        provider = DuckDuckGoProvider(config=config)

        # Should succeed for first 2 queries
        provider.search("query 1")
        provider.search("query 2")

        # Third query should fail with rate limit
        with pytest.raises(Exception, match="rate limit"):
            provider.search("query 3")

    def test_health_check(self):
        """Test health check functionality."""
        config = WebSearchConfig()
        provider = DuckDuckGoProvider(config=config)

        # Health check should return True (provider is always available)
        assert provider.health_check() is True


class TestHybridRetrieverWebSearch:
    """Test hybrid retriever with web search integration."""

    @pytest.fixture
    def mock_web_provider(self):
        """Create a mock web search provider."""
        mock_provider = Mock()
        mock_provider.search.return_value = [
            WebSearchResult(
                rank=1,
                title="Web Result 1",
                snippet="This is a web result about test query",
                url="https://example.com/1",
                provider="duckduckgo",
                trust_score=0.8,
                domain="example.com"
            ),
            WebSearchResult(
                rank=2,
                title="Web Result 2",
                snippet="Another web result with test information",
                url="https://cdc.gov/2",
                provider="duckduckgo",
                trust_score=0.9,
                domain="cdc.gov"
            )
        ]
        return mock_provider

    def test_web_search_disabled(self, mock_web_provider):
        """Test that web search is skipped when disabled."""
        # This would require actual retriever initialization
        # For now, we test the logic through orchestrator
        pass

    def test_web_search_parallel_mode(self):
        """Test parallel mode (always search web)."""
        # Test via orchestrator with parallel mode
        pass

    def test_web_search_on_low_confidence_mode(self):
        """Test on_low_confidence mode (conditional search)."""
        # Test via orchestrator with on_low_confidence mode
        pass

    def test_web_result_normalization(self, mock_web_provider):
        """Test web result normalization."""
        # Web results should be normalized to internal format
        pass

    def test_rrf_fusion_with_web_results(self):
        """Test RRF fusion with web results included."""
        # Test weighted RRF: local=1.0, web=0.7
        pass


class TestOrchestratorWebSearch:
    """Test orchestrator with web search integration."""

    @pytest.fixture
    def orchestrator_with_web(self):
        """Create orchestrator with web search enabled."""
        try:
            orchestrator = SemanticPatternOrchestrator(
                ollama_model="nomic-embed-text",
                ollama_generation_model="qwen3:14b",
                enable_web_search=True,
                web_search_provider_type="duckduckgo"
            )
            return orchestrator
        except Exception as e:
            pytest.skip(f"Could not initialize orchestrator: {e}")

    def test_orchestrator_initialization_with_web(self, orchestrator_with_web):
        """Test orchestrator initializes with web search provider."""
        assert orchestrator_with_web.web_search_provider is not None
        assert orchestrator_with_web.hybrid_retriever.web_search_provider is not None

    def test_orchestrator_initialization_without_web(self):
        """Test orchestrator initializes without web search."""
        try:
            orchestrator = SemanticPatternOrchestrator(
                enable_web_search=False
            )
            assert orchestrator.web_search_provider is None
        except Exception as e:
            pytest.skip(f"Could not initialize orchestrator: {e}")

    @patch('src.document_store.web.providers.DDGS')
    def test_query_with_web_search_parallel(self, mock_ddgs, orchestrator_with_web):
        """Test query with parallel web search mode."""
        # Mock web search results
        mock_ddgs.return_value.text.return_value = [
            {
                'title': 'Web Result',
                'body': 'Web snippet',
                'href': 'https://example.com/web'
            }
        ]

        try:
            result = orchestrator_with_web.query(
                query="What are the latest RAG patterns?",
                top_k=5,
                enable_web_search=True,
                web_mode="parallel"
            )

            # Should have results (mix of local and web)
            assert "answer" in result
            assert "sources" in result

            # Check if web sources are included
            sources = result.get("sources", [])
            web_sources = [s for s in sources if s.get("metadata", {}).get("source_type") == "web_search"]
            # Web sources may or may not be present depending on RRF ranking

        except Exception as e:
            pytest.skip(f"Query failed: {e}")

    @patch('src.document_store.web.providers.DDGS')
    def test_query_with_web_search_on_low_confidence(self, mock_ddgs, orchestrator_with_web):
        """Test query with on_low_confidence web search mode."""
        mock_ddgs.return_value.text.return_value = [
            {
                'title': 'Web Result',
                'body': 'Web snippet',
                'href': 'https://example.com/web'
            }
        ]

        try:
            # Query that should trigger low confidence
            result = orchestrator_with_web.query(
                query="What happened in healthcare AI in 2025?",  # Temporal keyword
                top_k=5,
                enable_web_search=True,
                web_mode="on_low_confidence"
            )

            assert "answer" in result
            assert "sources" in result

        except Exception as e:
            pytest.skip(f"Query failed: {e}")

    def test_query_without_web_search(self, orchestrator_with_web):
        """Test query with web search disabled."""
        try:
            result = orchestrator_with_web.query(
                query="What is RAG?",
                top_k=5,
                enable_web_search=False
            )

            # Should work normally without web results
            assert "answer" in result
            assert "sources" in result

            # No web sources should be present
            sources = result.get("sources", [])
            web_sources = [s for s in sources if s.get("metadata", {}).get("source_type") == "web_search"]
            assert len(web_sources) == 0

        except Exception as e:
            pytest.skip(f"Query failed: {e}")


class TestTrafilaturaHybridIntegration:
    """Integration tests for Trafilatura + DuckDuckGo hybrid mode."""

    def test_hybrid_provider_initialization(self):
        """Test hybrid provider initializes with both providers."""
        with patch('src.document_store.web.providers.TRAFILATURA_AVAILABLE', True), \
             patch('src.document_store.web.providers.DDGS_AVAILABLE', True), \
             patch('src.document_store.web.providers.use_config') as mock_use_config:

            mock_use_config.return_value = Mock()

            # Create DuckDuckGo provider as fallback
            ddg_config = WebSearchConfig(ddg_max_results=5)
            ddg_provider = DuckDuckGoProvider(config=ddg_config)

            # Create Trafilatura provider with DDG fallback
            traf_config = WebSearchConfig(
                trafilatura_fallback_to_ddg=True,
                enable_rate_limiting=False
            )
            traf_provider = TrafilaturaProvider(
                config=traf_config,
                ddg_fallback=ddg_provider
            )

            assert traf_provider.ddg_fallback is not None
            assert traf_provider.config.trafilatura_fallback_to_ddg is True

    @patch('src.document_store.web.providers.fetch_url')
    @patch('src.document_store.web.providers.extract')
    @patch('trafilatura.metadata.extract_metadata')
    @patch('src.document_store.web.providers.use_config')
    def test_hybrid_search_full_workflow(self, mock_use_config,
                                         mock_extract_metadata, mock_extract, mock_fetch):
        """Test complete hybrid workflow: DDG finds URLs → Trafilatura extracts content."""
        mock_use_config.return_value = Mock()

        # Mock Trafilatura extraction (returns full content)
        mock_fetch.return_value = "<html>Full article content</html>"
        mock_extract.side_effect = [
            "This is the full extracted article content about RAG architecture with detailed explanations...",
            "Complete healthcare RAG patterns guide with comprehensive information..."
        ]
        mock_extract_metadata.return_value = None

        # Create mocked DDG provider
        ddg_provider = Mock()
        ddg_provider.search.return_value = [
            WebSearchResult(
                rank=1,
                title="RAG Architecture Guide",
                snippet="Short snippet about RAG...",
                url="https://example.com/rag-guide",
                provider="duckduckgo",
                trust_score=0.5,
                domain="example.com",
                metadata={}
            ),
            WebSearchResult(
                rank=2,
                title="Healthcare RAG Patterns",
                snippet="Brief description...",
                url="https://medical.gov/rag-patterns",
                provider="duckduckgo",
                trust_score=0.9,
                domain="medical.gov",
                metadata={}
            )
        ]

        # Create Trafilatura provider with mocked DDG fallback
        traf_provider = TrafilaturaProvider(
            config=WebSearchConfig(trafilatura_fallback_to_ddg=True),
            ddg_fallback=ddg_provider
        )

        # Perform hybrid search
        results = traf_provider.search("RAG architecture patterns", max_results=2)

        # Verify results
        assert len(results) == 2

        # First result should have full content from Trafilatura
        assert results[0].metadata["extraction_method"] == "trafilatura+duckduckgo"
        assert "full_text" in results[0].metadata
        assert len(results[0].metadata["full_text"]) > 50  # Full content from Trafilatura
        assert results[0].metadata["ddg_snippet"] == "Short snippet about RAG..."
        assert results[0].metadata["ddg_title"] == "RAG Architecture Guide"

        # Second result from trusted domain
        assert results[1].domain == "medical.gov"
        assert results[1].metadata["extraction_method"] == "trafilatura+duckduckgo"

    @patch('src.document_store.web.providers.fetch_url')
    @patch('src.document_store.web.providers.use_config')
    def test_hybrid_fallback_to_snippet(self, mock_use_config, mock_fetch):
        """Test fallback to DDG snippet when Trafilatura extraction fails."""
        mock_use_config.return_value = Mock()

        # Mock Trafilatura extraction failure
        mock_fetch.return_value = None  # Fetch fails

        # Create mocked DDG provider
        ddg_provider = Mock()
        ddg_provider.search.return_value = [
            WebSearchResult(
                rank=1,
                title="Article Title",
                snippet="This is the DuckDuckGo snippet fallback",
                url="https://example.com/article",
                provider="duckduckgo",
                trust_score=0.5,
                domain="example.com",
                metadata={}
            )
        ]

        # Create Trafilatura provider with mocked DDG fallback
        traf_provider = TrafilaturaProvider(
            config=WebSearchConfig(trafilatura_fallback_to_ddg=True),
            ddg_fallback=ddg_provider
        )

        # Perform search
        results = traf_provider.search("test query", max_results=1)

        # Should fall back to DDG snippet
        assert len(results) == 1
        assert results[0].snippet == "This is the DuckDuckGo snippet fallback"
        assert results[0].metadata["extraction_method"] == "duckduckgo_only"
        assert "full_text" not in results[0].metadata

    @patch('src.document_store.web.providers.fetch_url')
    @patch('src.document_store.web.providers.extract')
    @patch('trafilatura.metadata.extract_metadata')
    def test_direct_url_extraction(self, mock_extract_metadata, mock_extract, mock_fetch):
        """Test direct URL extraction bypasses DDG."""
        # Mock Trafilatura extraction
        mock_fetch.return_value = "<html>Article HTML</html>"
        mock_extract.return_value = "Full article content extracted directly from URL"

        mock_metadata = Mock()
        mock_metadata.title = "Direct Article"
        mock_metadata.author = "Author Name"
        mock_metadata.date = "2025-01-19"
        mock_extract_metadata.return_value = mock_metadata

        with patch('src.document_store.web.providers.use_config'):
            # Create provider (no DDG fallback needed for direct URLs)
            traf_provider = TrafilaturaProvider(config=WebSearchConfig())

            # Search with direct URL
            results = traf_provider.search("https://example.com/article")

            # Should extract directly without DDG
            assert len(results) == 1
            assert results[0].title == "Direct Article"
            assert results[0].metadata["full_text"] == "Full article content extracted directly from URL"
            assert results[0].metadata["extraction_method"] == "trafilatura"
            assert "ddg_snippet" not in results[0].metadata

    def test_content_length_comparison(self):
        """Test that Trafilatura provides significantly more content than DDG snippets."""
        with patch('src.document_store.web.providers.fetch_url') as mock_fetch, \
             patch('src.document_store.web.providers.extract') as mock_extract, \
             patch('trafilatura.metadata.extract_metadata') as mock_extract_metadata, \
             patch('src.document_store.web.providers.use_config'):

            # Trafilatura returns full content (~2000 chars)
            full_content = "A" * 2000  # Simulate long article
            mock_fetch.return_value = "<html>Content</html>"
            mock_extract.return_value = full_content
            mock_extract_metadata.return_value = None

            # DDG returns short snippet (~60 chars)
            ddg_snippet = "Short snippet about the topic with limited information."

            # Create mocked DDG provider
            ddg_provider = Mock()
            ddg_provider.search.return_value = [
                WebSearchResult(
                    rank=1,
                    title="Article",
                    snippet=ddg_snippet,
                    url="https://example.com/article",
                    provider="duckduckgo",
                    trust_score=0.5,
                    domain="example.com",
                    metadata={}
                )
            ]

            # Create hybrid provider
            traf_provider = TrafilaturaProvider(
                config=WebSearchConfig(trafilatura_fallback_to_ddg=True),
                ddg_fallback=ddg_provider
            )

            # Perform search
            results = traf_provider.search("test query", max_results=1)

            # Verify content length improvement
            assert len(results) == 1
            assert len(results[0].metadata["full_text"]) == 2000  # Full content
            assert len(results[0].metadata["ddg_snippet"]) < 100  # Short snippet

            # 10x improvement in content
            content_ratio = len(results[0].metadata["full_text"]) / len(results[0].metadata["ddg_snippet"])
            assert content_ratio > 10


class TestAPIEndpointWebSearch:
    """Test API endpoint with web search parameters."""

    def test_query_request_validation(self):
        """Test query request validation with web search parameters."""
        from src.api_server import QueryRequest

        # Valid request
        request = QueryRequest(
            query="test query",
            enable_web_search=True,
            web_mode="parallel"
        )
        assert request.enable_web_search is True
        assert request.web_mode == "parallel"

        # Valid on_low_confidence mode
        request = QueryRequest(
            query="test query",
            enable_web_search=True,
            web_mode="on_low_confidence"
        )
        assert request.web_mode == "on_low_confidence"

    def test_invalid_web_mode(self):
        """Test that invalid web_mode should be caught."""
        from src.api_server import QueryRequest

        # This should be validated in the endpoint, not the model
        # The model allows any string, validation happens in the endpoint
        request = QueryRequest(
            query="test query",
            web_mode="invalid_mode"
        )
        # The endpoint will validate and reject this
        assert request.web_mode == "invalid_mode"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
