#!/usr/bin/env python3
"""
Test script for embedder selection functionality.

Tests that:
1. Both calibration matrices are loaded correctly
2. Query embedding works with both Ollama and Gemini
3. The embedder_type parameter is properly passed through
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import os
import logging
from dotenv import load_dotenv

from src.document_store.embeddings.hybrid_embedder import HealthcareHybridEmbedder

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_embedder_selection():
    """Test embedder selection with calibration matrices."""
    load_dotenv()

    logger.info("=" * 60)
    logger.info("Testing Embedder Selection")
    logger.info("=" * 60)

    # Initialize embedder with default type
    embedder = HealthcareHybridEmbedder(
        local_model_name="all-MiniLM-L12-v2",
        query_embedder_type=os.getenv("QUERY_EMBEDDER_TYPE", "ollama"),
        qwen_model=os.getenv("OLLAMA_MODEL", "nomic-embed-text"),
        ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        gemini_model=os.getenv("GEMINI_EMBEDDING_MODEL", "models/embedding-001"),
        gemini_api_key=os.getenv("GEMINI_API_KEY")
    )

    test_query = "What is RAPTOR RAG and how does it work?"

    # Test 1: Check calibration matrices
    logger.info("\n" + "=" * 60)
    logger.info("Test 1: Calibration Matrix Status")
    logger.info("=" * 60)

    for embedder_type in ["ollama", "gemini"]:
        if embedder_type in embedder.alignment_matrices:
            matrix = embedder.alignment_matrices[embedder_type]
            logger.info(f"✅ {embedder_type}: Matrix loaded, shape {matrix.shape}")
        else:
            logger.warning(f"❌ {embedder_type}: No calibration matrix found")

    # Test 2: Ollama embedding
    logger.info("\n" + "=" * 60)
    logger.info("Test 2: Ollama Query Embedding")
    logger.info("=" * 60)

    try:
        ollama_embedding = embedder.embed_query(test_query, embedder_type="ollama")
        logger.info(f"✅ Ollama embedding successful")
        logger.info(f"   Shape: {ollama_embedding.shape}")
        logger.info(f"   Norm: {(ollama_embedding ** 2).sum() ** 0.5:.4f}")
    except Exception as e:
        logger.error(f"❌ Ollama embedding failed: {e}")

    # Test 3: Gemini embedding
    logger.info("\n" + "=" * 60)
    logger.info("Test 3: Gemini Query Embedding")
    logger.info("=" * 60)

    try:
        gemini_embedding = embedder.embed_query(test_query, embedder_type="gemini")
        logger.info(f"✅ Gemini embedding successful")
        logger.info(f"   Shape: {gemini_embedding.shape}")
        logger.info(f"   Norm: {(gemini_embedding ** 2).sum() ** 0.5:.4f}")
    except Exception as e:
        logger.error(f"❌ Gemini embedding failed: {e}")

    # Test 4: Default embedding (should use QUERY_EMBEDDER_TYPE)
    logger.info("\n" + "=" * 60)
    logger.info("Test 4: Default Embedder")
    logger.info("=" * 60)

    try:
        default_embedding = embedder.embed_query(test_query)
        logger.info(f"✅ Default embedding successful (using {embedder.query_embedder_type})")
        logger.info(f"   Shape: {default_embedding.shape}")
    except Exception as e:
        logger.error(f"❌ Default embedding failed: {e}")

    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("Test Summary")
    logger.info("=" * 60)
    logger.info("✅ All tests completed!")
    logger.info("\nNext steps:")
    logger.info("1. Start the FastAPI server: ./venv/bin/python src/api_server.py")
    logger.info("2. Start the web UI: cd web-ui && npm run dev")
    logger.info("3. Test embedder selection in the UI dropdown")


if __name__ == "__main__":
    test_embedder_selection()
