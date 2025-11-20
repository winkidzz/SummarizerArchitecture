#!/usr/bin/env python3
"""
Unit Tests for Web Knowledge Base (Phase 2)

Tests the WebKnowledgeBaseManager class including:
- Initialization and collection creation
- Content hashing (SHA256)
- Citation generation (APA format)
- Configuration management
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.document_store.web.knowledge_base import (
    WebKnowledgeBaseManager,
    WebKnowledgeBaseConfig,
    WebKnowledgeDocument
)


class TestWebKnowledgeBaseConfig:
    """Test WebKnowledgeBaseConfig dataclass."""

    def test_config_default_values(self):
        """Test default configuration values."""
        config = WebKnowledgeBaseConfig()

        assert config.qdrant_url == "http://localhost:6333"
        assert config.collection_name == "web_knowledge"
        assert config.vector_size == 768
        assert config.ttl_days == 30
        assert config.max_documents == 10000  # Correct field name
        assert config.enable_auto_ingest is True
        assert config.tier_weight == 0.9

    def test_config_custom_values(self):
        """Test custom configuration values."""
        config = WebKnowledgeBaseConfig(
            qdrant_url="http://custom:6333",
            collection_name="custom_kb",
            vector_size=384,
            ttl_days=60,
            max_documents=5000,  # Correct field name
            enable_auto_ingest=False,
            tier_weight=0.8
        )

        assert config.qdrant_url == "http://custom:6333"
        assert config.collection_name == "custom_kb"
        assert config.vector_size == 384
        assert config.ttl_days == 60
        assert config.max_documents == 5000
        assert config.enable_auto_ingest is False
        assert config.tier_weight == 0.8


class TestWebKnowledgeDocument:
    """Test WebKnowledgeDocument dataclass."""

    def test_document_creation_minimal(self):
        """Test document creation with required fields."""
        doc = WebKnowledgeDocument(
            id="test-id-123",
            content="Test content",
            embedding=[0.1, 0.2, 0.3],
            url="https://example.com",
            domain="example.com",
            title="Test Title"
        )

        assert doc.id == "test-id-123"
        assert doc.content == "Test content"
        assert doc.url == "https://example.com"
        assert doc.domain == "example.com"
        assert doc.title == "Test Title"
        assert doc.trust_score == 0.5  # Default value

    def test_document_with_optional_fields(self):
        """Test document with all optional fields."""
        doc = WebKnowledgeDocument(
            id="test-id-456",
            content="Test content",
            embedding=[0.1, 0.2],
            url="https://example.com",
            domain="example.com",
            title="Test Title",
            author="Test Author",
            content_date="2024-01-01",
            trust_score=0.9,
            times_retrieved=5,
            citation_text="Example citation"
        )

        assert doc.domain == "example.com"
        assert doc.author == "Test Author"
        assert doc.trust_score == 0.9
        assert doc.times_retrieved == 5
        assert doc.citation_text == "Example citation"


class TestWebKnowledgeBaseManagerInitialization:
    """Test WebKnowledgeBaseManager initialization."""

    @patch('src.document_store.web.knowledge_base.QdrantClient')
    def test_init_default_config(self, mock_qdrant_client):
        """Test initialization with default configuration."""
        mock_embedder = Mock()
        mock_embedder.embed_query.return_value = [0.1] * 768

        config = WebKnowledgeBaseConfig()
        manager = WebKnowledgeBaseManager(config=config, embedder=mock_embedder)

        assert manager.config == config
        assert manager.embedder == mock_embedder
        mock_qdrant_client.assert_called_once_with(url=config.qdrant_url)

    @patch('src.document_store.web.knowledge_base.QdrantClient')
    def test_collection_creation(self, mock_qdrant_client):
        """Test that collection is created on initialization."""
        mock_client_instance = MagicMock()
        mock_qdrant_client.return_value = mock_client_instance

        # Mock get_collections() to return empty list
        mock_collections = MagicMock()
        mock_collections.collections = []
        mock_client_instance.get_collections.return_value = mock_collections

        mock_embedder = Mock()
        config = WebKnowledgeBaseConfig(vector_size=384)
        manager = WebKnowledgeBaseManager(config=config, embedder=mock_embedder)

        # Verify collection check was attempted
        mock_client_instance.get_collections.assert_called()

    @patch('src.document_store.web.knowledge_base.QdrantClient')
    def test_collection_already_exists(self, mock_qdrant_client):
        """Test behavior when collection already exists."""
        mock_client_instance = MagicMock()
        mock_qdrant_client.return_value = mock_client_instance

        # Mock get_collections() to return collection
        mock_collection = MagicMock()
        mock_collection.name = "web_knowledge"
        mock_collections = MagicMock()
        mock_collections.collections = [mock_collection]
        mock_client_instance.get_collections.return_value = mock_collections

        mock_embedder = Mock()
        config = WebKnowledgeBaseConfig()
        manager = WebKnowledgeBaseManager(config=config, embedder=mock_embedder)

        # Should check if collection exists
        mock_client_instance.get_collections.assert_called()


class TestContentHashing:
    """Test content hashing functionality."""

    @patch('src.document_store.web.knowledge_base.QdrantClient')
    def test_content_hash_generation(self, mock_qdrant_client):
        """Test SHA256 content hash generation."""
        mock_embedder = Mock()
        config = WebKnowledgeBaseConfig()
        manager = WebKnowledgeBaseManager(config=config, embedder=mock_embedder)

        content1 = "This is test content"
        content2 = "This is different content"
        content3 = "This is test content"  # Same as content1

        hash1 = manager._calculate_content_hash(content1)
        hash2 = manager._calculate_content_hash(content2)
        hash3 = manager._calculate_content_hash(content3)

        # Same content should produce same hash
        assert hash1 == hash3
        # Different content should produce different hash
        assert hash1 != hash2
        # Hash should be 64 characters (SHA256 hex)
        assert len(hash1) == 64
        assert len(hash2) == 64
        # Hash should be alphanumeric
        assert hash1.isalnum()

    @patch('src.document_store.web.knowledge_base.QdrantClient')
    def test_content_hash_deterministic(self, mock_qdrant_client):
        """Test that content hashing is deterministic."""
        mock_embedder = Mock()
        config = WebKnowledgeBaseConfig()
        manager = WebKnowledgeBaseManager(config=config, embedder=mock_embedder)

        content = "Deterministic test content"

        # Generate hash multiple times
        hash1 = manager._calculate_content_hash(content)
        hash2 = manager._calculate_content_hash(content)
        hash3 = manager._calculate_content_hash(content)

        # All should be identical
        assert hash1 == hash2 == hash3


class TestCitationGeneration:
    """Test citation generation functionality."""

    @patch('src.document_store.web.knowledge_base.QdrantClient')
    def test_apa_citation_complete(self, mock_qdrant_client):
        """Test APA citation generation with all fields."""
        mock_embedder = Mock()
        config = WebKnowledgeBaseConfig()
        manager = WebKnowledgeBaseManager(config=config, embedder=mock_embedder)

        citation = manager._generate_citation(
            title="Test Article About RAG",
            url="https://example.com/article",
            author="John Doe",
            content_date="2024-01-15"  # Correct parameter name
        )

        # Citation should contain key elements
        assert isinstance(citation, str)
        assert len(citation) > 0
        # Should contain the URL
        assert "https://example.com/article" in citation

    @patch('src.document_store.web.knowledge_base.QdrantClient')
    def test_apa_citation_minimal(self, mock_qdrant_client):
        """Test APA citation with minimal fields."""
        mock_embedder = Mock()
        config = WebKnowledgeBaseConfig()
        manager = WebKnowledgeBaseManager(config=config, embedder=mock_embedder)

        citation = manager._generate_citation(
            title="Test Article",
            url="https://example.com/article",
            author=None,
            content_date=None  # Correct parameter name
        )

        # Should still generate valid citation
        assert isinstance(citation, str)
        assert len(citation) > 0
        assert "https://example.com/article" in citation


class TestStatistics:
    """Test statistics and analytics."""

    @patch('src.document_store.web.knowledge_base.QdrantClient')
    def test_get_stats(self, mock_qdrant_client):
        """Test getting collection statistics."""
        mock_client_instance = MagicMock()
        mock_qdrant_client.return_value = mock_client_instance
        mock_client_instance.collection_exists.return_value = True

        # Mock collection info
        mock_info = MagicMock()
        mock_info.points_count = 100
        mock_info.vectors_count = 100
        mock_client_instance.get_collection.return_value = mock_info

        mock_embedder = Mock()
        config = WebKnowledgeBaseConfig()
        manager = WebKnowledgeBaseManager(config=config, embedder=mock_embedder)

        stats = manager.get_stats()

        assert stats["collection_name"] == "web_knowledge"
        assert stats["total_documents"] == 100


class TestConfigurationFlexibility:
    """Test configuration flexibility and edge cases."""

    def test_config_ttl_edge_cases(self):
        """Test TTL configuration with edge cases."""
        # Very short TTL
        config1 = WebKnowledgeBaseConfig(ttl_days=1)
        assert config1.ttl_days == 1

        # Very long TTL
        config2 = WebKnowledgeBaseConfig(ttl_days=365)
        assert config2.ttl_days == 365

    def test_config_vector_dimensions(self):
        """Test different vector dimensions."""
        # Small dimension (local model)
        config1 = WebKnowledgeBaseConfig(vector_size=384)
        assert config1.vector_size == 384

        # Large dimension (premium model)
        config2 = WebKnowledgeBaseConfig(vector_size=1536)
        assert config2.vector_size == 1536

    def test_config_tier_weights(self):
        """Test tier weight configuration."""
        # Lower weight
        config1 = WebKnowledgeBaseConfig(tier_weight=0.5)
        assert config1.tier_weight == 0.5

        # Higher weight (closer to Pattern Library)
        config2 = WebKnowledgeBaseConfig(tier_weight=0.95)
        assert config2.tier_weight == 0.95


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
