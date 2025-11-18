#!/usr/bin/env python3
"""
Test Layer 6: RAG Generation

Tests the RAG generation system with:
- Context window management
- Citation tracking
- Integration with hybrid retrieval
- Ollama Qwen generation
"""

import sys
from pathlib import Path
import time
import numpy as np
import uuid

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.document_store.generation.rag_generator import HealthcareRAGGenerator
from src.document_store.search.hybrid_retriever import HealthcareHybridRetriever
from src.document_store.search.two_step_retrieval import TwoStepRetrieval
from src.document_store.search.bm25_search import BM25Search
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
    
    # Check Ollama
    for i in range(30):
        try:
            urllib.request.urlopen("http://localhost:11434/api/tags", timeout=2)
            logger.info("✅ Ollama is ready")
            break
        except:
            if i < 29:
                time.sleep(1)
            else:
                logger.warning("⚠️  Ollama may not be ready")


def setup_test_data(vector_store, bm25_search, embedder):
    """Set up test data in both Qdrant and Elasticsearch."""
    # Create test chunks with more detailed content
    test_docs = [
        {
            "text": "RAPTOR RAG (Recursive Abstractive Processing for Tree-Organized Retrieval) is an advanced retrieval technique that uses recursive clustering to organize documents hierarchically. It creates a tree structure where parent nodes contain summaries of child nodes, enabling efficient retrieval at multiple levels of abstraction.",
            "doc_id": "doc_1",
            "doc_type": "rag_pattern",
            "title": "RAPTOR RAG Pattern"
        },
        {
            "text": "Hybrid retrieval combines vector search with keyword search using BM25. Vector search captures semantic similarity, while BM25 captures exact keyword matches. The two approaches are combined using Reciprocal Rank Fusion (RRF) to get the best of both worlds.",
            "doc_id": "doc_2",
            "doc_type": "rag_pattern",
            "title": "Hybrid Retrieval Pattern"
        },
        {
            "text": "Semantic chunking preserves document structure and context. Unlike simple text splitting, semantic chunking identifies logical boundaries like paragraphs, sections, and code blocks. This ensures that chunks maintain their semantic meaning and context.",
            "doc_id": "doc_3",
            "doc_type": "chunking_pattern",
            "title": "Semantic Chunking Pattern"
        },
        {
            "text": "Vector databases store embeddings for fast similarity search. They use approximate nearest neighbor algorithms to find similar vectors quickly, even in high-dimensional spaces. Popular vector databases include Qdrant, Pinecone, and Weaviate.",
            "doc_id": "doc_4",
            "doc_type": "storage_pattern",
            "title": "Vector Database Pattern"
        },
        {
            "text": "Reciprocal Rank Fusion (RRF) combines multiple search result rankings. It assigns scores based on the reciprocal of the rank position in each result set. This allows combining results from different search methods without requiring score normalization.",
            "doc_id": "doc_5",
            "doc_type": "fusion_pattern",
            "title": "RRF Fusion Pattern"
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
                "chunk_id": str(uuid.uuid4()),
                "title": doc.get("title", "")
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
    
    # Index in Elasticsearch
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


def test_rag_generation_basic():
    """Test basic RAG generation."""
    logger.info("=" * 80)
    logger.info("Testing Layer 6: Basic RAG Generation")
    logger.info("=" * 80)
    
    try:
        embedder = HealthcareHybridEmbedder()
        vector_store = HealthcareVectorStore(
            url="http://localhost:6333",
            collection_name="test_rag_generation",
            vector_size=384
        )
        bm25_search = BM25Search(
            url="http://localhost:9200",
            index_name="test_rag_generation"
        )
        
        # Setup test data
        wait_for_services()
        setup_test_data(vector_store, bm25_search, embedder)
        
        # Setup hybrid retriever
        two_step = TwoStepRetrieval(embedder, vector_store)
        hybrid_retriever = HealthcareHybridRetriever(
            two_step_retriever=two_step,
            bm25_search=bm25_search
        )
        
        # Setup RAG generator
        rag_generator = HealthcareRAGGenerator(
            model="qwen3:14b"
        )
        
        query = "What is RAPTOR RAG?"
        # Retrieve documents first
        retrieved_docs = hybrid_retriever.retrieve(query, top_k=5)
        result = rag_generator.generate(query, docs=retrieved_docs)
        
        logger.info(f"✅ RAG generation successful!")
        logger.info(f"   Query: {query}")
        logger.info(f"   Answer length: {len(result.get('answer', ''))} characters")
        logger.info(f"   Sources: {len(result.get('sources', []))}")
        logger.info(f"   Context docs used: {result.get('context_docs_used', 0)}")
        logger.info(f"   Total docs retrieved: {result.get('total_docs_retrieved', 0)}")
        
        # Log answer preview
        answer = result.get('answer', '')
        if answer:
            logger.info(f"\n   Answer preview: {answer[:200]}...")
        
        # Log sources
        sources = result.get('sources', [])
        if sources:
            logger.info(f"\n   Sources:")
            for i, source in enumerate(sources[:3]):
                logger.info(f"   {i+1}. {source.get('source_path', source.get('document_id', 'N/A'))}")
        
        assert 'answer' in result, "Result should contain answer"
        assert len(result.get('answer', '')) > 0, "Answer should not be empty"
        assert 'sources' in result, "Result should contain sources"
        
        logger.info("✅ All assertions passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ RAG generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_context_window_management():
    """Test context window management."""
    logger.info("\n" + "=" * 80)
    logger.info("Testing Layer 6: Context Window Management")
    logger.info("=" * 80)
    
    try:
        embedder = HealthcareHybridEmbedder()
        vector_store = HealthcareVectorStore(
            url="http://localhost:6333",
            collection_name="test_rag_generation",
            vector_size=384
        )
        bm25_search = BM25Search(
            url="http://localhost:9200",
            index_name="test_rag_generation"
        )
        
        # Setup test data
        setup_test_data(vector_store, bm25_search, embedder)
        
        two_step = TwoStepRetrieval(embedder, vector_store)
        hybrid_retriever = HealthcareHybridRetriever(
            two_step_retriever=two_step,
            bm25_search=bm25_search
        )
        
        rag_generator_small = HealthcareRAGGenerator(
            model="qwen3:14b",
            max_context_tokens=200
        )
        rag_generator_large = HealthcareRAGGenerator(
            model="qwen3:14b",
            max_context_tokens=2000
        )
        
        query = "Explain hybrid retrieval and RRF"
        
        # Retrieve documents
        retrieved_docs = hybrid_retriever.retrieve(query, top_k=10)
        
        # Test with small context window
        result_small = rag_generator_small.generate(query, docs=retrieved_docs)
        
        # Test with larger context window
        result_large = rag_generator_large.generate(query, docs=retrieved_docs)
        
        logger.info(f"✅ Context window management successful!")
        logger.info(f"   Small context (200 tokens):")
        logger.info(f"   - Docs used: {result_small.get('context_docs_used', 0)}")
        logger.info(f"   - Answer length: {len(result_small.get('answer', ''))}")
        logger.info(f"   Large context (2000 tokens):")
        logger.info(f"   - Docs used: {result_large.get('context_docs_used', 0)}")
        logger.info(f"   - Answer length: {len(result_large.get('answer', ''))}")
        
        # Verify that larger context uses more docs
        assert result_large.get('context_docs_used', 0) >= result_small.get('context_docs_used', 0), \
            "Larger context should use at least as many docs"
        
        logger.info("✅ All assertions passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Context window management failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_citation_tracking():
    """Test citation tracking."""
    logger.info("\n" + "=" * 80)
    logger.info("Testing Layer 6: Citation Tracking")
    logger.info("=" * 80)
    
    try:
        embedder = HealthcareHybridEmbedder()
        vector_store = HealthcareVectorStore(
            url="http://localhost:6333",
            collection_name="test_rag_generation",
            vector_size=384
        )
        bm25_search = BM25Search(
            url="http://localhost:9200",
            index_name="test_rag_generation"
        )
        
        # Setup test data
        setup_test_data(vector_store, bm25_search, embedder)
        
        two_step = TwoStepRetrieval(embedder, vector_store)
        hybrid_retriever = HealthcareHybridRetriever(
            two_step_retriever=two_step,
            bm25_search=bm25_search
        )
        
        rag_generator = HealthcareRAGGenerator(
            model="qwen3:14b"
        )
        
        query = "What are the different RAG patterns?"
        retrieved_docs = hybrid_retriever.retrieve(query, top_k=5)
        result = rag_generator.generate(query, docs=retrieved_docs)
        
        logger.info(f"✅ Citation tracking successful!")
        logger.info(f"   Query: {query}")
        
        sources = result.get('sources', [])
        logger.info(f"   Total sources: {len(sources)}")
        
        # Log source details
        for i, source in enumerate(sources):
            logger.info(f"\n   Source {i+1}:")
            logger.info(f"   - Document ID: {source.get('document_id', 'N/A')}")
            logger.info(f"   - Source Path: {source.get('source_path', 'N/A')}")
            logger.info(f"   - Document Type: {source.get('document_type', 'N/A')}")
        
        # Verify sources have required fields
        for source in sources:
            assert 'document_id' in source or 'source_path' in source, \
                "Source should have document_id or source_path"
        
        logger.info("✅ All assertions passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Citation tracking failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_integration_with_retrieval():
    """Test integration with hybrid retrieval."""
    logger.info("\n" + "=" * 80)
    logger.info("Testing Layer 6: Integration with Hybrid Retrieval")
    logger.info("=" * 80)
    
    try:
        embedder = HealthcareHybridEmbedder()
        vector_store = HealthcareVectorStore(
            url="http://localhost:6333",
            collection_name="test_rag_generation",
            vector_size=384
        )
        bm25_search = BM25Search(
            url="http://localhost:9200",
            index_name="test_rag_generation"
        )
        
        # Setup test data
        setup_test_data(vector_store, bm25_search, embedder)
        
        two_step = TwoStepRetrieval(embedder, vector_store)
        hybrid_retriever = HealthcareHybridRetriever(
            two_step_retriever=two_step,
            bm25_search=bm25_search
        )
        
        rag_generator = HealthcareRAGGenerator(
            model="qwen3:14b"
        )
        
        query = "How does semantic chunking work?"
        
        # Retrieve documents
        retrieved_docs = hybrid_retriever.retrieve(query, top_k=5)
        
        # Generate response
        result = rag_generator.generate(query, docs=retrieved_docs)
        
        logger.info(f"✅ Integration test successful!")
        logger.info(f"   Query: {query}")
        logger.info(f"   Answer generated: {len(result.get('answer', '')) > 0}")
        logger.info(f"   Context docs used: {result.get('context_docs_used', 0)}")
        logger.info(f"   Sources: {len(result.get('sources', []))}")
        
        # Verify integration
        assert 'answer' in result, "Should have answer"
        assert 'context_docs_used' in result, "Should have context_docs_used"
        assert 'sources' in result, "Should have sources"
        assert result.get('context_docs_used', 0) > 0, "Should have at least one context doc"
        
        logger.info("✅ All assertions passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def cleanup_test_data():
    """Clean up test collections."""
    try:
        vector_store = HealthcareVectorStore(
            url="http://localhost:6333",
            collection_name="test_rag_generation",
            vector_size=384
        )
        vector_store.delete_collection()
        logger.info("✅ Test collection cleaned up")
    except Exception as e:
        logger.warning(f"Could not clean up test collection: {e}")


if __name__ == "__main__":
    logger.info("Starting Layer 6 Tests...\n")
    
    wait_for_services()
    
    results = []
    results.append(test_rag_generation_basic())
    results.append(test_context_window_management())
    results.append(test_citation_tracking())
    results.append(test_integration_with_retrieval())
    
    logger.info("\n" + "=" * 80)
    logger.info("Layer 6 Test Summary")
    logger.info("=" * 80)
    logger.info(f"Passed: {sum(results)}/{len(results)}")
    
    # Cleanup
    if all(results):
        logger.info("\nCleaning up test data...")
        cleanup_test_data()
    
    if all(results):
        logger.info("✅ All Layer 6 tests passed!")
        sys.exit(0)
    else:
        logger.error("❌ Some Layer 6 tests failed!")
        sys.exit(1)

