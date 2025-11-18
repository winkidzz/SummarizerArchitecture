#!/usr/bin/env python3
"""
Test Layer 5: Hybrid Retrieval

Tests the hybrid retrieval system combining:
- Two-step vector search
- BM25 keyword search
- Reciprocal Rank Fusion
- Cross-encoder reranking
"""

import sys
from pathlib import Path
import time
import numpy as np
import uuid

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.document_store.search.two_step_retrieval import TwoStepRetrieval
from src.document_store.search.bm25_search import BM25Search
from src.document_store.search.hybrid_retriever import HealthcareHybridRetriever
from src.document_store.embeddings.hybrid_embedder import HealthcareHybridEmbedder
from src.document_store.storage.qdrant_store import HealthcareVectorStore
from src.document_store.processors.semantic_chunker import Chunk
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def wait_for_services():
    """Wait for all services to be ready."""
    import urllib.request
    
    # Check Qdrant
    for i in range(30):
        try:
            urllib.request.urlopen("http://localhost:6333/", timeout=2)
            logger.info("✅ Qdrant is ready")
            break
        except:
            if i < 29:
                time.sleep(1)
            else:
                logger.warning("⚠️  Qdrant may not be ready")
    
    # Check Elasticsearch
    for i in range(30):
        try:
            urllib.request.urlopen("http://localhost:9200/_cluster/health", timeout=2)
            logger.info("✅ Elasticsearch is ready")
            break
        except:
            if i < 29:
                time.sleep(1)
            else:
                logger.warning("⚠️  Elasticsearch may not be ready")


def setup_test_data(vector_store, bm25_search, embedder):
    """Set up test data in both Qdrant and Elasticsearch."""
    # Create test chunks
    test_docs = [
        {
            "text": "RAPTOR RAG is a retrieval technique that uses recursive clustering.",
            "doc_id": "doc_1",
            "doc_type": "rag_pattern"
        },
        {
            "text": "Hybrid retrieval combines vector search with keyword search using BM25.",
            "doc_id": "doc_2",
            "doc_type": "rag_pattern"
        },
        {
            "text": "Semantic chunking preserves document structure and context.",
            "doc_id": "doc_3",
            "doc_type": "chunking_pattern"
        },
        {
            "text": "Vector databases store embeddings for fast similarity search.",
            "doc_id": "doc_4",
            "doc_type": "storage_pattern"
        },
        {
            "text": "Reciprocal Rank Fusion combines multiple search result rankings.",
            "doc_id": "doc_5",
            "doc_type": "fusion_pattern"
        }
    ]
    
    chunks = []
    for doc in test_docs:
        chunk = Chunk(
            text=doc["text"],
            metadata={
                "document_id": doc["doc_id"],
                "document_type": doc["doc_type"],
                "section_type": "text",
                "source_path": f"{doc['doc_id']}.md",
                "chunk_id": str(uuid.uuid4())
            },
            chunk_index=0
        )
        chunks.append(chunk)
    
    # Generate embeddings
    texts = [chunk.text for chunk in chunks]
    embeddings = embedder.embed_documents(texts)
    
    # Upsert to Qdrant
    vector_store.upsert_documents(chunks, embeddings)
    logger.info(f"✅ Upserted {len(chunks)} documents to Qdrant")
    
    # Index in Elasticsearch (if provided)
    if bm25_search is not None:
        es_docs = [
            {
                "id": chunk.metadata["chunk_id"],
                "text": chunk.text,
                "metadata": chunk.metadata
            }
            for chunk in chunks
        ]
        bm25_search.index_documents(es_docs)
        logger.info(f"✅ Indexed {len(es_docs)} documents in Elasticsearch")
    
    return chunks


def test_two_step_retrieval():
    """Test two-step vector retrieval."""
    logger.info("=" * 80)
    logger.info("Testing Layer 5: Two-Step Vector Retrieval")
    logger.info("=" * 80)
    
    try:
        embedder = HealthcareHybridEmbedder()
        vector_store = HealthcareVectorStore(
            url="http://localhost:6333",
            collection_name="test_hybrid_retrieval",
            vector_size=384
        )
        
        # Setup test data
        wait_for_services()
        setup_test_data(vector_store, None, embedder)
        
        two_step = TwoStepRetrieval(embedder, vector_store)
        
        query = "What is RAPTOR RAG?"
        results = two_step.retrieve(query, top_k_approximate=10, top_k_final=3)
        
        logger.info(f"✅ Two-step retrieval successful!")
        logger.info(f"   Query: {query}")
        logger.info(f"   Results returned: {len(results)}")
        
        for i, result in enumerate(results[:3]):
            logger.info(f"\n   Result {i+1}:")
            logger.info(f"   - Score: {result.get('similarity_score', result.get('score', 0)):.4f}")
            logger.info(f"   - Text: {result['text'][:60]}...")
        
        assert len(results) > 0, "Should return at least one result"
        
        logger.info("✅ All assertions passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Two-step retrieval failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_bm25_search():
    """Test BM25 keyword search."""
    logger.info("\n" + "=" * 80)
    logger.info("Testing Layer 5: BM25 Keyword Search")
    logger.info("=" * 80)
    
    try:
        bm25_search = BM25Search(
            url="http://localhost:9200",
            index_name="test_hybrid_retrieval"
        )
        
        embedder = HealthcareHybridEmbedder()
        vector_store = HealthcareVectorStore(
            url="http://localhost:6333",
            collection_name="test_hybrid_retrieval",
            vector_size=384
        )
        
        # Setup test data
        setup_test_data(vector_store, bm25_search, embedder)
        
        query = "vector database"
        results = bm25_search.search(query, k=3)
        
        logger.info(f"✅ BM25 search successful!")
        logger.info(f"   Query: {query}")
        logger.info(f"   Results returned: {len(results)}")
        
        for i, result in enumerate(results):
            logger.info(f"\n   Result {i+1}:")
            logger.info(f"   - Score: {result['score']:.4f}")
            logger.info(f"   - Text: {result['text'][:60]}...")
        
        assert len(results) > 0, "Should return at least one result"
        assert all('score' in r for r in results), "All results should have scores"
        
        logger.info("✅ All assertions passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ BM25 search failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_hybrid_retriever():
    """Test hybrid retriever combining vector and BM25."""
    logger.info("\n" + "=" * 80)
    logger.info("Testing Layer 5: Hybrid Retriever (Vector + BM25 + RRF)")
    logger.info("=" * 80)
    
    try:
        embedder = HealthcareHybridEmbedder()
        vector_store = HealthcareVectorStore(
            url="http://localhost:6333",
            collection_name="test_hybrid_retrieval",
            vector_size=384
        )
        bm25_search = BM25Search(
            url="http://localhost:9200",
            index_name="test_hybrid_retrieval"
        )
        
        # Setup test data
        setup_test_data(vector_store, bm25_search, embedder)
        
        two_step = TwoStepRetrieval(embedder, vector_store)
        hybrid_retriever = HealthcareHybridRetriever(
            two_step_retriever=two_step,
            bm25_search=bm25_search,
            rrf_constant=60
        )
        
        query = "retrieval technique"
        results = hybrid_retriever.retrieve(query, top_k=5)
        
        logger.info(f"✅ Hybrid retrieval successful!")
        logger.info(f"   Query: {query}")
        logger.info(f"   Results returned: {len(results)}")
        
        for i, result in enumerate(results):
            logger.info(f"\n   Result {i+1}:")
            logger.info(f"   - RRF Score: {result.get('rrf_score', 'N/A')}")
            logger.info(f"   - Similarity: {result.get('similarity_score', result.get('score', 0)):.4f}")
            logger.info(f"   - Method: {result.get('ranking_method', 'N/A')}")
            logger.info(f"   - Text: {result['text'][:60]}...")
        
        assert len(results) > 0, "Should return at least one result"
        assert any('rrf_score' in r for r in results), "Results should have RRF scores"
        
        logger.info("✅ All assertions passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Hybrid retrieval failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_rrf_fusion():
    """Test Reciprocal Rank Fusion."""
    logger.info("\n" + "=" * 80)
    logger.info("Testing Layer 5: Reciprocal Rank Fusion")
    logger.info("=" * 80)
    
    try:
        embedder = HealthcareHybridEmbedder()
        vector_store = HealthcareVectorStore(
            url="http://localhost:6333",
            collection_name="test_hybrid_retrieval",
            vector_size=384
        )
        bm25_search = BM25Search(
            url="http://localhost:9200",
            index_name="test_hybrid_retrieval"
        )
        
        # Setup test data
        chunks = setup_test_data(vector_store, bm25_search, embedder)
        
        two_step = TwoStepRetrieval(embedder, vector_store)
        hybrid_retriever = HealthcareHybridRetriever(
            two_step_retriever=two_step,
            bm25_search=bm25_search
        )
        
        query = "RAPTOR clustering"
        
        # Get separate results
        vector_results = two_step.retrieve(query, top_k_approximate=10, top_k_final=5)
        bm25_results = bm25_search.search(query, k=5)
        
        # Test RRF fusion
        fused = hybrid_retriever._rrf_fusion(vector_results, bm25_results)
        
        logger.info(f"✅ RRF fusion successful!")
        logger.info(f"   Vector results: {len(vector_results)}")
        logger.info(f"   BM25 results: {len(bm25_results)}")
        logger.info(f"   Fused results: {len(fused)}")
        
        # Check that fused results have RRF scores
        for i, result in enumerate(fused[:3]):
            logger.info(f"\n   Fused Result {i+1}:")
            logger.info(f"   - RRF Score: {result.get('rrf_score', 0):.6f}")
            logger.info(f"   - Text: {result['text'][:50]}...")
        
        assert len(fused) > 0, "Should have fused results"
        assert all('rrf_score' in r for r in fused), "All fused results should have RRF scores"
        
        # Check that RRF scores are reasonable (should be positive)
        rrf_scores = [r.get('rrf_score', 0) for r in fused]
        assert all(score > 0 for score in rrf_scores), "RRF scores should be positive"
        
        logger.info("✅ All assertions passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ RRF fusion failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def cleanup_test_data():
    """Clean up test collections."""
    try:
        vector_store = HealthcareVectorStore(
            url="http://localhost:6333",
            collection_name="test_hybrid_retrieval",
            vector_size=384
        )
        vector_store.delete_collection()
        logger.info("✅ Test collection cleaned up")
    except Exception as e:
        logger.warning(f"Could not clean up test collection: {e}")


if __name__ == "__main__":
    logger.info("Starting Layer 5 Tests...\n")
    
    wait_for_services()
    
    results = []
    results.append(test_two_step_retrieval())
    results.append(test_bm25_search())
    results.append(test_rrf_fusion())
    results.append(test_hybrid_retriever())
    
    logger.info("\n" + "=" * 80)
    logger.info("Layer 5 Test Summary")
    logger.info("=" * 80)
    logger.info(f"Passed: {sum(results)}/{len(results)}")
    
    # Cleanup
    if all(results):
        logger.info("\nCleaning up test data...")
        cleanup_test_data()
    
    if all(results):
        logger.info("✅ All Layer 5 tests passed!")
        sys.exit(0)
    else:
        logger.error("❌ Some Layer 5 tests failed!")
        sys.exit(1)

