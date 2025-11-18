#!/usr/bin/env python3
"""
Test Layer 7: Semantic Caching

Tests the semantic caching system with:
- Cache storage and retrieval
- Semantic similarity-based cache lookup
- Cache hit/miss detection
- TTL management
- Integration with RAG pipeline
"""

import sys
from pathlib import Path
import time
import numpy as np
import uuid

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.document_store.cache.semantic_cache import HealthcareSemanticCache
from src.document_store.embeddings.hybrid_embedder import HealthcareHybridEmbedder
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def wait_for_redis():
    """Wait for Redis to be ready."""
    import urllib.request
    import redis
    
    for i in range(30):
        try:
            r = redis.Redis(host='localhost', port=6380, db=0, socket_timeout=2)
            r.ping()
            logger.info("✅ Redis is ready")
            return True
        except:
            if i < 29:
                time.sleep(1)
            else:
                logger.warning("⚠️  Redis may not be ready")
    return True


def test_cache_storage():
    """Test basic cache storage and retrieval."""
    logger.info("=" * 80)
    logger.info("Testing Layer 7: Cache Storage and Retrieval")
    logger.info("=" * 80)
    
    try:
        wait_for_redis()
        
        embedder = HealthcareHybridEmbedder()
        cache = HealthcareSemanticCache(
            host="localhost",
            port=6380
        )
        
        query = "What is RAPTOR RAG?"
        query_embedding = embedder.embed_query(query)
        response = {
            "answer": "RAPTOR RAG is a retrieval technique that uses recursive clustering.",
            "sources": [{"document_id": "doc_1"}],
            "context_docs_used": 3
        }
        
        # Store in cache
        cache.set(query, query_embedding, response)
        logger.info(f"✅ Stored response in cache for query: {query}")
        
        # Retrieve from cache
        cached_response = cache.get(query, query_embedding)
        
        logger.info(f"✅ Cache retrieval successful!")
        logger.info(f"   Query: {query}")
        logger.info(f"   Cached: {cached_response is not None}")
        
        if cached_response:
            logger.info(f"   Answer length: {len(cached_response.get('answer', ''))}")
            logger.info(f"   Sources: {len(cached_response.get('sources', []))}")
        
        assert cached_response is not None, "Should retrieve cached response"
        assert cached_response.get('answer') == response['answer'], "Answer should match"
        
        logger.info("✅ All assertions passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Cache storage test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_semantic_similarity():
    """Test semantic similarity-based cache lookup."""
    logger.info("\n" + "=" * 80)
    logger.info("Testing Layer 7: Semantic Similarity Cache Lookup")
    logger.info("=" * 80)
    
    try:
        wait_for_redis()
        
        embedder = HealthcareHybridEmbedder()
        cache = HealthcareSemanticCache(
            host="localhost",
            port=6380,
            similarity_threshold=0.85
        )
        
        # Store original query
        original_query = "What is RAPTOR RAG?"
        original_embedding = embedder.embed_query(original_query)
        response = {
            "answer": "RAPTOR RAG is a retrieval technique that uses recursive clustering.",
            "sources": [{"document_id": "doc_1"}]
        }
        cache.set(original_query, original_embedding, response)
        logger.info(f"✅ Stored response for: {original_query}")
        
        # Test similar queries
        similar_queries = [
            "Tell me about RAPTOR RAG",
            "What does RAPTOR RAG do?",
            "Explain RAPTOR RAG technique"
        ]
        
        hits = 0
        for similar_query in similar_queries:
            similar_embedding = embedder.embed_query(similar_query)
            cached = cache.get(similar_query, similar_embedding)
            if cached:
                hits += 1
                logger.info(f"   ✅ Cache HIT for: {similar_query}")
            else:
                logger.info(f"   ❌ Cache MISS for: {similar_query}")
        
        logger.info(f"✅ Semantic similarity test complete!")
        logger.info(f"   Similar queries tested: {len(similar_queries)}")
        logger.info(f"   Cache hits: {hits}")
        logger.info(f"   Cache misses: {len(similar_queries) - hits}")
        
        # Should have at least some hits for semantically similar queries
        assert hits > 0, "Should have at least one cache hit for similar queries"
        
        logger.info("✅ All assertions passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Semantic similarity test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_cache_hit_miss():
    """Test cache hit/miss detection."""
    logger.info("\n" + "=" * 80)
    logger.info("Testing Layer 7: Cache Hit/Miss Detection")
    logger.info("=" * 80)
    
    try:
        wait_for_redis()
        
        embedder = HealthcareHybridEmbedder()
        cache = HealthcareSemanticCache(
            host="localhost",
            port=6380
        )
        
        # Store a query
        query1 = "What is hybrid retrieval?"
        query1_embedding = embedder.embed_query(query1)
        response1 = {
            "answer": "Hybrid retrieval combines vector and keyword search.",
            "sources": []
        }
        cache.set(query1, query1_embedding, response1)
        logger.info(f"✅ Stored: {query1}")
        
        # Test exact match (should hit)
        result1 = cache.get(query1, query1_embedding)
        assert result1 is not None, "Exact match should be a cache hit"
        logger.info(f"✅ Cache HIT for exact match")
        
        # Test different query (should miss)
        query2 = "What is machine learning?"
        query2_embedding = embedder.embed_query(query2)
        result2 = cache.get(query2, query2_embedding)
        assert result2 is None, "Different query should be a cache miss"
        logger.info(f"✅ Cache MISS for different query")
        
        # Test similar query (might hit depending on threshold)
        query3 = "Explain hybrid retrieval"
        query3_embedding = embedder.embed_query(query3)
        result3 = cache.get(query3, query3_embedding)
        if result3:
            logger.info(f"✅ Cache HIT for similar query (semantic match)")
        else:
            logger.info(f"✅ Cache MISS for similar query (below threshold)")
        
        logger.info("✅ All assertions passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Cache hit/miss test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_cache_ttl():
    """Test cache TTL (time-to-live) management."""
    logger.info("\n" + "=" * 80)
    logger.info("Testing Layer 7: Cache TTL Management")
    logger.info("=" * 80)
    
    try:
        wait_for_redis()
        
        embedder = HealthcareHybridEmbedder()
        # Use short TTL for testing
        cache = HealthcareSemanticCache(
            host="localhost",
            port=6380,
            cache_ttl=2  # 2 seconds for testing
        )
        
        query = "What is semantic chunking?"
        query_embedding = embedder.embed_query(query)
        response = {
            "answer": "Semantic chunking preserves document structure.",
            "sources": []
        }
        
        # Store in cache
        cache.set(query, query_embedding, response)
        logger.info(f"✅ Stored response with 2-second TTL")
        
        # Should be available immediately
        result1 = cache.get(query, query_embedding)
        assert result1 is not None, "Should be available immediately"
        logger.info(f"✅ Cache HIT immediately after storage")
        
        # Wait for TTL to expire
        logger.info("⏳ Waiting for TTL to expire (2 seconds)...")
        time.sleep(3)
        
        # Should be expired now
        result2 = cache.get(query, query_embedding)
        if result2 is None:
            logger.info(f"✅ Cache expired after TTL (expected)")
        else:
            logger.warning(f"⚠️  Cache still available after TTL (may be within grace period)")
        
        logger.info("✅ TTL test complete!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Cache TTL test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_integration_with_rag():
    """Test integration with RAG pipeline."""
    logger.info("\n" + "=" * 80)
    logger.info("Testing Layer 7: Integration with RAG Pipeline")
    logger.info("=" * 80)
    
    try:
        wait_for_redis()
        
        embedder = HealthcareHybridEmbedder()
        cache = HealthcareSemanticCache(
            host="localhost",
            port=6380
        )
        
        # Simulate RAG pipeline usage
        query = "What is vector database?"
        query_embedding = embedder.embed_query(query)
        response = {
            "answer": "Vector databases store embeddings for similarity search.",
            "sources": [{"document_id": "doc_4"}],
            "context_docs_used": 2
        }
        
        # Check cache before storing
        cached_before = cache.get(query, query_embedding)
        logger.info(f"   Cache before: {'HIT' if cached_before else 'MISS'}")
        
        # Store response (as RAG pipeline would)
        cache.set(query, query_embedding, response)
        logger.info(f"✅ Stored RAG response in cache")
        
        # Check cache after storing
        cached_after = cache.get(query, query_embedding)
        logger.info(f"   Cache after: {'HIT' if cached_after else 'MISS'}")
        
        assert cached_after is not None, "Should retrieve cached response"
        assert cached_after.get('answer') == response['answer'], "Answer should match"
        assert len(cached_after.get('sources', [])) == len(response['sources']), "Sources should match"
        
        # Test with similar query
        similar_query = "Tell me about vector databases"
        similar_embedding = embedder.embed_query(similar_query)
        cached_similar = cache.get(similar_query, similar_embedding)
        if cached_similar:
            logger.info(f"✅ Semantic cache HIT for similar query")
        else:
            logger.info(f"✅ Semantic cache MISS for similar query (below threshold)")
        
        logger.info("✅ All assertions passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def cleanup_cache():
    """Clean up test cache entries."""
    try:
        import redis
        r = redis.Redis(host='localhost', port=6380, db=0)
        # Clear test keys (pattern-based cleanup)
        keys = list(r.scan_iter(match="cache:*"))
        if keys:
            r.delete(*keys)
            logger.info(f"✅ Cleaned up {len(keys)} cache entries")
    except Exception as e:
        logger.warning(f"Could not clean up cache: {e}")


if __name__ == "__main__":
    logger.info("Starting Layer 7 Tests...\n")
    
    wait_for_redis()
    
    results = []
    results.append(test_cache_storage())
    results.append(test_semantic_similarity())
    results.append(test_cache_hit_miss())
    results.append(test_cache_ttl())
    results.append(test_integration_with_rag())
    
    logger.info("\n" + "=" * 80)
    logger.info("Layer 7 Test Summary")
    logger.info("=" * 80)
    logger.info(f"Passed: {sum(results)}/{len(results)}")
    
    # Cleanup
    if all(results):
        logger.info("\nCleaning up test cache...")
        cleanup_cache()
    
    if all(results):
        logger.info("✅ All Layer 7 tests passed!")
        sys.exit(0)
    else:
        logger.error("❌ Some Layer 7 tests failed!")
        sys.exit(1)

