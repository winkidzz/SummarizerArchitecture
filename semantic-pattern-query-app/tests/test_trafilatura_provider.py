#!/usr/bin/env python3
"""
Unit tests for TrafilaturaProvider.

Tests the Trafilatura web content extraction provider with mocked dependencies.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import List, Dict, Any
import time

# Import the classes we're testing
from src.document_store.web.providers import (
    TrafilaturaProvider,
    DuckDuckGoProvider,
    WebSearchConfig,
    WebSearchResult
)


class TestTrafilaturaProviderInitialization:
    """Test TrafilaturaProvider initialization."""

    def test_init_default_config(self):
        """Test initialization with default config."""
        with patch('src.document_store.web.providers.TRAFILATURA_AVAILABLE', True):
            with patch('src.document_store.web.providers.use_config') as mock_use_config:
                mock_config_obj = MagicMock()
                mock_use_config.return_value = mock_config_obj

                provider = TrafilaturaProvider()

                assert provider.config is not None
                assert provider.ddg_fallback is None
                assert provider._query_count == 0
                assert provider._last_query_time is None
                mock_config_obj.set.assert_called_once()

    def test_init_custom_config(self):
        """Test initialization with custom config."""
        config = WebSearchConfig(
            trafilatura_timeout=20,
            trafilatura_favor_recall=False,
            max_queries_per_minute=5
        )

        with patch('src.document_store.web.providers.TRAFILATURA_AVAILABLE', True):
            with patch('src.document_store.web.providers.use_config') as mock_use_config:
                mock_config_obj = MagicMock()
                mock_use_config.return_value = mock_config_obj

                provider = TrafilaturaProvider(config=config)

                assert provider.config.trafilatura_timeout == 20
                assert provider.config.trafilatura_favor_recall is False
                assert provider.config.max_queries_per_minute == 5

    def test_init_with_ddg_fallback(self):
        """Test initialization with DuckDuckGo fallback."""
        ddg_provider = Mock(spec=DuckDuckGoProvider)

        with patch('src.document_store.web.providers.TRAFILATURA_AVAILABLE', True):
            with patch('src.document_store.web.providers.use_config'):
                provider = TrafilaturaProvider(ddg_fallback=ddg_provider)

                assert provider.ddg_fallback is ddg_provider

    def test_init_trafilatura_not_available(self):
        """Test initialization fails when Trafilatura not installed."""
        with patch('src.document_store.web.providers.TRAFILATURA_AVAILABLE', False):
            with pytest.raises(ImportError, match="trafilatura package is not installed"):
                TrafilaturaProvider()


class TestTrafilaturaProviderURLDetection:
    """Test URL detection helper method."""

    def setup_method(self):
        """Set up test provider."""
        with patch('src.document_store.web.providers.TRAFILATURA_AVAILABLE', True):
            with patch('src.document_store.web.providers.use_config'):
                self.provider = TrafilaturaProvider()

    def test_is_url_http(self):
        """Test HTTP URL detection."""
        assert self.provider._is_url("http://example.com") is True

    def test_is_url_https(self):
        """Test HTTPS URL detection."""
        assert self.provider._is_url("https://example.com") is True

    def test_is_not_url_plain_text(self):
        """Test plain text is not detected as URL."""
        assert self.provider._is_url("search query text") is False

    def test_is_not_url_domain_only(self):
        """Test domain without protocol is not detected as URL."""
        assert self.provider._is_url("example.com") is False


class TestTrafilaturaDomainExtraction:
    """Test domain extraction helper method."""

    def setup_method(self):
        """Set up test provider."""
        with patch('src.document_store.web.providers.TRAFILATURA_AVAILABLE', True):
            with patch('src.document_store.web.providers.use_config'):
                self.provider = TrafilaturaProvider()

    def test_extract_domain_https(self):
        """Test domain extraction from HTTPS URL."""
        domain = self.provider._extract_domain("https://www.example.com/path/to/page")
        assert domain == "www.example.com"

    def test_extract_domain_http(self):
        """Test domain extraction from HTTP URL."""
        domain = self.provider._extract_domain("http://example.org/article")
        assert domain == "example.org"

    def test_extract_domain_with_port(self):
        """Test domain extraction with port number."""
        domain = self.provider._extract_domain("https://example.com:8080/page")
        assert domain == "example.com:8080"

    def test_extract_domain_subdomain(self):
        """Test domain extraction with subdomain."""
        domain = self.provider._extract_domain("https://blog.example.com/post")
        assert domain == "blog.example.com"


class TestTrafilaturaTrustScoring:
    """Test trust scoring calculation."""

    def setup_method(self):
        """Set up test provider with trust scoring enabled."""
        config = WebSearchConfig(
            enable_trust_scoring=True,
            trusted_domains=[".gov", ".edu", ".org"],
            blocked_domains=["spam.com", "malicious.net"]
        )

        with patch('src.document_store.web.providers.TRAFILATURA_AVAILABLE', True):
            with patch('src.document_store.web.providers.use_config'):
                self.provider = TrafilaturaProvider(config=config)

    def test_trust_score_trusted_gov(self):
        """Test trust score for .gov domain."""
        score = self.provider._calculate_trust_score(
            "www.example.gov",
            "Government Article",
            "Sample content"
        )
        assert score == 0.9

    def test_trust_score_trusted_edu(self):
        """Test trust score for .edu domain."""
        score = self.provider._calculate_trust_score(
            "university.edu",
            "Academic Paper",
            "Research content"
        )
        assert score == 0.9

    def test_trust_score_trusted_org(self):
        """Test trust score for .org domain."""
        score = self.provider._calculate_trust_score(
            "nonprofit.org",
            "Article Title",
            "Content snippet"
        )
        assert score == 0.9

    def test_trust_score_blocked_domain(self):
        """Test trust score for blocked domain."""
        score = self.provider._calculate_trust_score(
            "spam.com",
            "Spam Title",
            "Spam content"
        )
        assert score == 0.0

    def test_trust_score_default(self):
        """Test default trust score for unknown domain."""
        score = self.provider._calculate_trust_score(
            "example.com",
            "Article Title",
            "Content snippet"
        )
        assert score == 0.5

    def test_trust_score_disabled(self):
        """Test trust scoring when disabled."""
        config = WebSearchConfig(enable_trust_scoring=False)

        with patch('src.document_store.web.providers.TRAFILATURA_AVAILABLE', True):
            with patch('src.document_store.web.providers.use_config'):
                provider = TrafilaturaProvider(config=config)

                score = provider._calculate_trust_score(
                    "www.example.gov",
                    "Title",
                    "Content"
                )
                assert score == 0.5  # Neutral score


class TestTrafilaturaContentExtraction:
    """Test content extraction from URLs."""

    def setup_method(self):
        """Set up test provider."""
        with patch('src.document_store.web.providers.TRAFILATURA_AVAILABLE', True):
            with patch('src.document_store.web.providers.use_config'):
                self.provider = TrafilaturaProvider()

    @patch('src.document_store.web.providers.fetch_url')
    @patch('src.document_store.web.providers.extract')
    @patch('trafilatura.metadata.extract_metadata')
    def test_extract_from_url_success(self, mock_extract_metadata, mock_extract, mock_fetch):
        """Test successful content extraction from URL."""
        # Mock successful fetch and extraction
        mock_fetch.return_value = "<html>Downloaded content</html>"
        mock_extract.return_value = "Extracted article text with full content"

        # Mock metadata
        mock_metadata = Mock()
        mock_metadata.title = "Article Title"
        mock_metadata.author = "John Doe"
        mock_metadata.date = "2025-01-19"
        mock_extract_metadata.return_value = mock_metadata

        results = self.provider._extract_from_url("https://example.com/article")

        assert len(results) == 1
        result = results[0]
        assert result.title == "Article Title"
        assert result.url == "https://example.com/article"
        assert result.provider == "trafilatura"
        assert result.domain == "example.com"
        assert "full_text" in result.metadata
        assert result.metadata["full_text"] == "Extracted article text with full content"
        assert result.metadata["author"] == "John Doe"
        assert result.metadata["date"] == "2025-01-19"
        assert result.metadata["extraction_method"] == "trafilatura"

    @patch('src.document_store.web.providers.fetch_url')
    def test_extract_from_url_fetch_fails(self, mock_fetch):
        """Test extraction when URL fetch fails."""
        mock_fetch.return_value = None

        results = self.provider._extract_from_url("https://example.com/article")

        assert results == []

    @patch('src.document_store.web.providers.fetch_url')
    @patch('src.document_store.web.providers.extract')
    def test_extract_from_url_no_content(self, mock_extract, mock_fetch):
        """Test extraction when no content extracted."""
        mock_fetch.return_value = "<html>Downloaded content</html>"
        mock_extract.return_value = None

        results = self.provider._extract_from_url("https://example.com/article")

        assert results == []

    @patch('src.document_store.web.providers.fetch_url')
    @patch('src.document_store.web.providers.extract')
    @patch('trafilatura.metadata.extract_metadata')
    def test_extract_from_url_long_content(self, mock_extract_metadata, mock_extract, mock_fetch):
        """Test extraction creates snippet from long content."""
        long_text = "A" * 1000  # 1000 characters
        mock_fetch.return_value = "<html>Downloaded content</html>"
        mock_extract.return_value = long_text
        mock_extract_metadata.return_value = None

        results = self.provider._extract_from_url("https://example.com/article")

        assert len(results) == 1
        result = results[0]
        assert len(result.snippet) == 503  # 500 + "..."
        assert result.snippet.endswith("...")
        assert result.metadata["full_text"] == long_text

    @patch('src.document_store.web.providers.fetch_url')
    def test_extract_from_url_exception(self, mock_fetch):
        """Test graceful handling of exceptions."""
        mock_fetch.side_effect = Exception("Network error")

        results = self.provider._extract_from_url("https://example.com/article")

        assert results == []


class TestTrafilaturaMultipleURLs:
    """Test extraction from multiple URLs."""

    def setup_method(self):
        """Set up test provider."""
        with patch('src.document_store.web.providers.TRAFILATURA_AVAILABLE', True):
            with patch('src.document_store.web.providers.use_config'):
                self.provider = TrafilaturaProvider()

    @patch('src.document_store.web.providers.fetch_url')
    @patch('src.document_store.web.providers.extract')
    @patch('trafilatura.metadata.extract_metadata')
    def test_search_urls_multiple(self, mock_extract_metadata, mock_extract, mock_fetch):
        """Test extraction from multiple URLs."""
        urls = [
            "https://example.com/article1",
            "https://example.com/article2",
            "https://example.com/article3"
        ]

        mock_fetch.return_value = "<html>Content</html>"
        mock_extract.side_effect = ["Text 1", "Text 2", "Text 3"]
        mock_extract_metadata.return_value = None

        results = self.provider.search_urls(urls)

        assert len(results) == 3
        assert results[0].rank == 1
        assert results[1].rank == 2
        assert results[2].rank == 3
        assert results[0].url == urls[0]
        assert results[1].url == urls[1]
        assert results[2].url == urls[2]

    @patch('src.document_store.web.providers.fetch_url')
    @patch('src.document_store.web.providers.extract')
    def test_search_urls_partial_failure(self, mock_extract, mock_fetch):
        """Test extraction when some URLs fail."""
        urls = [
            "https://example.com/article1",
            "https://example.com/article2",
            "https://example.com/article3"
        ]

        # First succeeds, second fails, third succeeds
        mock_fetch.side_effect = ["<html>1</html>", None, "<html>3</html>"]
        mock_extract.side_effect = ["Text 1", "Text 3"]

        results = self.provider.search_urls(urls)

        # Only 2 results (1 and 3)
        assert len(results) == 2
        assert results[0].url == urls[0]
        assert results[1].url == urls[2]


class TestTrafilaturaHybridSearch:
    """Test hybrid search with DuckDuckGo fallback."""

    def setup_method(self):
        """Set up test provider with DDG fallback."""
        with patch('src.document_store.web.providers.TRAFILATURA_AVAILABLE', True):
            with patch('src.document_store.web.providers.use_config'):
                self.ddg_provider = Mock(spec=DuckDuckGoProvider)
                config = WebSearchConfig(
                    trafilatura_fallback_to_ddg=True,
                    enable_rate_limiting=False
                )
                self.provider = TrafilaturaProvider(
                    config=config,
                    ddg_fallback=self.ddg_provider
                )

    @patch('src.document_store.web.providers.fetch_url')
    @patch('src.document_store.web.providers.extract')
    @patch('trafilatura.metadata.extract_metadata')
    def test_search_with_ddg_fallback_all_succeed(self, mock_extract_metadata,
                                                   mock_extract, mock_fetch):
        """Test hybrid search when all Trafilatura extractions succeed."""
        # Mock DuckDuckGo results
        ddg_results = [
            WebSearchResult(
                rank=1,
                title="DDG Title 1",
                snippet="DDG snippet 1",
                url="https://example.com/article1",
                provider="duckduckgo",
                trust_score=0.5,
                domain="example.com",
                metadata={}
            ),
            WebSearchResult(
                rank=2,
                title="DDG Title 2",
                snippet="DDG snippet 2",
                url="https://example.com/article2",
                provider="duckduckgo",
                trust_score=0.5,
                domain="example.com",
                metadata={}
            )
        ]
        self.ddg_provider.search.return_value = ddg_results

        # Mock Trafilatura extraction
        mock_fetch.return_value = "<html>Content</html>"
        mock_extract.side_effect = ["Full content 1", "Full content 2"]
        mock_extract_metadata.return_value = None

        results = self.provider.search("test query", max_results=2)

        assert len(results) == 2
        assert results[0].metadata["full_text"] == "Full content 1"
        assert results[0].metadata["extraction_method"] == "trafilatura+duckduckgo"
        assert results[0].metadata["ddg_snippet"] == "DDG snippet 1"
        assert results[0].metadata["ddg_title"] == "DDG Title 1"

    @patch('src.document_store.web.providers.fetch_url')
    def test_search_with_ddg_fallback_trafilatura_fails(self, mock_fetch):
        """Test hybrid search when Trafilatura extraction fails."""
        # Mock DuckDuckGo results
        ddg_results = [
            WebSearchResult(
                rank=1,
                title="DDG Title",
                snippet="DDG snippet",
                url="https://example.com/article",
                provider="duckduckgo",
                trust_score=0.5,
                domain="example.com",
                metadata={}
            )
        ]
        self.ddg_provider.search.return_value = ddg_results

        # Mock Trafilatura extraction failure
        mock_fetch.return_value = None

        results = self.provider.search("test query", max_results=1)

        # Should fall back to DDG snippet
        assert len(results) == 1
        assert "full_text" not in results[0].metadata
        assert results[0].metadata["extraction_method"] == "duckduckgo_only"
        assert results[0].snippet == "DDG snippet"

    def test_search_no_ddg_results(self):
        """Test hybrid search when DuckDuckGo returns no results."""
        self.ddg_provider.search.return_value = []

        results = self.provider.search("test query", max_results=5)

        assert results == []

    def test_search_url_direct_extraction(self):
        """Test that URL queries skip DDG and extract directly."""
        with patch.object(self.provider, '_extract_from_url') as mock_extract:
            mock_extract.return_value = [Mock(spec=WebSearchResult)]

            results = self.provider.search("https://example.com/article")

            # Should call _extract_from_url directly, not DDG
            mock_extract.assert_called_once()
            self.ddg_provider.search.assert_not_called()

    def test_search_no_fallback_configured(self):
        """Test search without DDG fallback returns empty."""
        config = WebSearchConfig(
            trafilatura_fallback_to_ddg=False,
            enable_rate_limiting=False
        )
        with patch('src.document_store.web.providers.use_config'):
            provider = TrafilaturaProvider(config=config, ddg_fallback=None)

        results = provider.search("test query")

        assert results == []


class TestTrafilaturaRateLimiting:
    """Test rate limiting functionality."""

    def setup_method(self):
        """Set up test provider with rate limiting enabled."""
        config = WebSearchConfig(
            enable_rate_limiting=True,
            max_queries_per_minute=3
        )

        with patch('src.document_store.web.providers.TRAFILATURA_AVAILABLE', True):
            with patch('src.document_store.web.providers.use_config'):
                self.provider = TrafilaturaProvider(config=config)

    def test_rate_limit_initial_state(self):
        """Test initial rate limit state."""
        assert self.provider._query_count == 0
        assert self.provider._last_query_time is None

    @patch('src.document_store.web.providers.time.sleep')
    @patch('src.document_store.web.providers.time.time')
    def test_rate_limit_within_limit(self, mock_time, mock_sleep):
        """Test queries within rate limit proceed normally."""
        mock_time.return_value = 1000.0

        # First query
        self.provider._check_rate_limit()
        assert self.provider._query_count == 1

        # Second query (within limit)
        self.provider._check_rate_limit()
        assert self.provider._query_count == 2

        # Third query (still within limit)
        self.provider._check_rate_limit()
        assert self.provider._query_count == 3

        # Should not sleep
        mock_sleep.assert_not_called()

    @patch('src.document_store.web.providers.time.sleep')
    @patch('src.document_store.web.providers.time.time')
    def test_rate_limit_exceeded(self, mock_time, mock_sleep):
        """Test rate limit triggers sleep when exceeded."""
        # Simulate 3 queries in first 30 seconds
        mock_time.return_value = 1000.0
        self.provider._check_rate_limit()  # Query 1
        self.provider._check_rate_limit()  # Query 2
        self.provider._check_rate_limit()  # Query 3

        # 4th query at 30 seconds (still in same minute)
        mock_time.return_value = 1030.0
        self.provider._check_rate_limit()  # Query 4 - should trigger sleep

        # Should sleep for ~30 seconds
        mock_sleep.assert_called_once()
        sleep_time = mock_sleep.call_args[0][0]
        assert 29 < sleep_time < 31

    @patch('src.document_store.web.providers.time.time')
    def test_rate_limit_resets_after_minute(self, mock_time):
        """Test rate limit counter resets after 60 seconds."""
        # 3 queries at t=1000
        mock_time.return_value = 1000.0
        self.provider._check_rate_limit()
        self.provider._check_rate_limit()
        self.provider._check_rate_limit()
        assert self.provider._query_count == 3

        # Query after 60+ seconds (t=1065)
        mock_time.return_value = 1065.0
        self.provider._check_rate_limit()

        # Counter should reset
        assert self.provider._query_count == 1


class TestTrafilaturaHealthCheck:
    """Test health check functionality."""

    def setup_method(self):
        """Set up test provider."""
        with patch('src.document_store.web.providers.TRAFILATURA_AVAILABLE', True):
            with patch('src.document_store.web.providers.use_config'):
                self.provider = TrafilaturaProvider()

    @patch('src.document_store.web.providers.fetch_url')
    @patch('src.document_store.web.providers.extract')
    def test_health_check_success(self, mock_extract, mock_fetch):
        """Test successful health check."""
        mock_fetch.return_value = "<html>Test content</html>"
        mock_extract.return_value = "Extracted text"

        result = self.provider.health_check()

        assert result is True

    @patch('src.document_store.web.providers.fetch_url')
    def test_health_check_fetch_fails(self, mock_fetch):
        """Test health check when fetch fails."""
        mock_fetch.return_value = None

        result = self.provider.health_check()

        assert result is False

    @patch('src.document_store.web.providers.fetch_url')
    def test_health_check_exception(self, mock_fetch):
        """Test health check with exception."""
        mock_fetch.side_effect = Exception("Network error")

        result = self.provider.health_check()

        assert result is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
