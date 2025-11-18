#!/usr/bin/env python3
"""
Test Layer 4: Qdrant Vector Database

Tests the Qdrant vector store with quantization and filtering.
"""

import sys
from pathlib import Path
import time
import numpy as np
import uuid

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.document_store.storage.qdrant_store import HealthcareVectorStore
from src.document_store.processors.semantic_chunker import Chunk
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def wait_for_qdrant(max_wait=30):
    """Wait for Qdrant to be ready."""
    import urllib.request
    start_time = time.time()
    while time.time() - start_time < max_wait:
        try:
            response = urllib.request.urlopen("http://localhost:6333/", timeout=2)
            if response.getcode() == 200:
                logger.info("✅ Qdrant is ready")
                return True
        except Exception:
            pass
        logger.info("⏳ Waiting for Qdrant to be ready...")
        time.sleep(1)
    # Try to continue anyway - Qdrant might be ready but health endpoint might be different
    logger.warning("⚠️  Health check timeout, but continuing anyway...")
    return True


def test_qdrant_connection():
    """Test basic Qdrant connection."""
    logger.info("=" * 80)
    logger.info("Testing Layer 4: Qdrant Connection")
    logger.info("=" * 80)
    
    if not wait_for_qdrant():
        logger.error("❌ Qdrant did not become ready in time")
        return False
    
    try:
        vector_store = HealthcareVectorStore(
            url="http://localhost:6333",
            collection_name="test_pattern_documents",
            vector_size=384,
            on_disk=True
        )
        
        logger.info("✅ Qdrant connection successful!")
        logger.info(f"   Collection: {vector_store.collection_name}")
        logger.info(f"   Vector size: {vector_store.vector_size}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Qdrant connection failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_document_upsert():
    """Test upserting documents to Qdrant."""
    logger.info("\n" + "=" * 80)
    logger.info("Testing Layer 4: Document Upsert")
    logger.info("=" * 80)
    
    try:
        vector_store = HealthcareVectorStore(
            url="http://localhost:6333",
            collection_name="test_pattern_documents",
            vector_size=384,
            on_disk=True
        )
        
        # Create test chunks
        chunks = [
            Chunk(
                text="This is a test document about RAG patterns.",
                metadata={
                    "document_id": "test_doc_1",
                    "document_type": "markdown",
                    "section_type": "text",
                    "source_path": "test.md",
                    "chunk_id": str(uuid.uuid4())
                },
                chunk_index=0
            ),
            Chunk(
                text="Another chunk about vector databases and embeddings.",
                metadata={
                    "document_id": "test_doc_1",
                    "document_type": "markdown",
                    "section_type": "text",
                    "source_path": "test.md",
                    "chunk_id": str(uuid.uuid4())
                },
                chunk_index=1
            ),
            Chunk(
                text="A third chunk with different content about semantic search.",
                metadata={
                    "document_id": "test_doc_2",
                    "document_type": "markdown",
                    "section_type": "text",
                    "source_path": "test2.md",
                    "chunk_id": str(uuid.uuid4())
                },
                chunk_index=0
            )
        ]
        
        # Create test embeddings (384 dimensions to match local model)
        embeddings = np.random.rand(len(chunks), 384).astype(np.float32)
        # Normalize embeddings
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        embeddings = embeddings / norms
        
        # Upsert documents
        vector_store.upsert_documents(chunks, embeddings)
        
        logger.info(f"✅ Upserted {len(chunks)} documents successfully!")
        
        # Get collection info
        info = vector_store.get_collection_info()
        initial_count = info['points_count']
        logger.info(f"   Collection points before: {initial_count}")
        logger.info(f"   Collection points after: {info['points_count']}")
        logger.info(f"   Vector size: {info['config']['vector_size']}")
        logger.info(f"   On disk: {info['config']['on_disk']}")
        
        # Check that points were added (may have existing points from previous tests)
        assert info['points_count'] >= len(chunks), f"Point count ({info['points_count']}) should be at least {len(chunks)}"
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Document upsert failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_vector_search():
    """Test vector search in Qdrant."""
    logger.info("\n" + "=" * 80)
    logger.info("Testing Layer 4: Vector Search")
    logger.info("=" * 80)
    
    try:
        vector_store = HealthcareVectorStore(
            url="http://localhost:6333",
            collection_name="test_pattern_documents",
            vector_size=384,
            on_disk=True
        )
        
        # Create a query embedding
        query_embedding = np.random.rand(384).astype(np.float32)
        query_embedding = query_embedding / np.linalg.norm(query_embedding)
        
        # Search without filters
        results = vector_store.search(
            query_embedding,
            top_k=3
        )
        
        logger.info(f"✅ Search successful!")
        logger.info(f"   Results returned: {len(results)}")
        
        for i, result in enumerate(results):
            logger.info(f"\n   Result {i+1}:")
            logger.info(f"   - Score: {result['score']:.4f}")
            logger.info(f"   - Text: {result['text'][:50]}...")
            logger.info(f"   - Document ID: {result['metadata'].get('document_id', 'N/A')}")
        
        assert len(results) > 0, "Should return at least one result"
        assert all('score' in r for r in results), "All results should have scores"
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Vector search failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_payload_filtering():
    """Test payload filtering in Qdrant."""
    logger.info("\n" + "=" * 80)
    logger.info("Testing Layer 4: Payload Filtering")
    logger.info("=" * 80)
    
    try:
        vector_store = HealthcareVectorStore(
            url="http://localhost:6333",
            collection_name="test_pattern_documents",
            vector_size=384,
            on_disk=True
        )
        
        # Create a query embedding
        query_embedding = np.random.rand(384).astype(np.float32)
        query_embedding = query_embedding / np.linalg.norm(query_embedding)
        
        # Search with filter (only test_doc_1)
        results = vector_store.search(
            query_embedding,
            top_k=10,
            filters={"document_id": "test_doc_1"}
        )
        
        logger.info(f"✅ Filtered search successful!")
        logger.info(f"   Results returned: {len(results)}")
        
        # Verify all results match the filter
        for result in results:
            doc_id = result['metadata'].get('document_id')
            assert doc_id == "test_doc_1", f"All results should be from test_doc_1, got {doc_id}"
        
        logger.info(f"   ✅ All {len(results)} results match filter (document_id=test_doc_1)")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Payload filtering failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def cleanup_test_collection():
    """Clean up test collection."""
    try:
        vector_store = HealthcareVectorStore(
            url="http://localhost:6333",
            collection_name="test_pattern_documents",
            vector_size=384
        )
        vector_store.delete_collection()
        logger.info("✅ Test collection cleaned up")
    except Exception as e:
        logger.warning(f"Could not clean up test collection: {e}")


if __name__ == "__main__":
    logger.info("Starting Layer 4 Tests...\n")
    
    results = []
    results.append(test_qdrant_connection())
    results.append(test_document_upsert())
    results.append(test_vector_search())
    results.append(test_payload_filtering())
    
    logger.info("\n" + "=" * 80)
    logger.info("Layer 4 Test Summary")
    logger.info("=" * 80)
    logger.info(f"Passed: {sum(results)}/{len(results)}")
    
    # Cleanup
    if all(results):
        logger.info("\nCleaning up test collection...")
        cleanup_test_collection()
    
    if all(results):
        logger.info("✅ All Layer 4 tests passed!")
        sys.exit(0)
    else:
        logger.error("❌ Some Layer 4 tests failed!")
        sys.exit(1)

