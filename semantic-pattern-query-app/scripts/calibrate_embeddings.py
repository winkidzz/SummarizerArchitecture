#!/usr/bin/env python3
"""
Calibration script for embedding models.

Calibrates premium embeddings (Gemini/Ollama) to local model space.
Run this once to create alignment matrices for each embedder type.
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

# Sample texts for calibration (should be representative of your domain)
SAMPLE_TEXTS = [
    "What is RAPTOR RAG and how does it work?",
    "Explain the hybrid retrieval pattern for healthcare documents.",
    "How do I implement semantic chunking for clinical notes?",
    "What are the best practices for RAG in healthcare?",
    "Compare vector search vs BM25 for medical document retrieval.",
    "Explain the two-step embedding strategy for cost optimization.",
    "How does Qdrant scalar quantization reduce memory usage?",
    "What is reciprocal rank fusion and when should I use it?",
    "Explain context window management for RAG generation.",
    "How does semantic caching improve query performance?",
    "What is the difference between basic RAG and advanced RAG patterns?",
    "How do I handle PHI in healthcare document processing?",
    "Explain the architecture of a production RAG system.",
    "What are the key metrics for evaluating RAG performance?",
    "How do I implement multi-vector retrieval?",
    "What is the role of cross-encoder reranking in hybrid retrieval?",
    "Explain document extraction strategies for PDFs.",
    "How do I optimize embedding costs in production?",
    "What are the trade-offs between different vector databases?",
    "How do I implement semantic chunking for structured documents?",
] * 5  # Repeat to get more samples (100 total)


def calibrate_gemini():
    """Calibrate Gemini embeddings to local model space."""
    logger.info("Calibrating Gemini embeddings...")
    
    try:
        embedder = HealthcareHybridEmbedder(
            local_model_name="all-MiniLM-L12-v2",
            query_embedder_type="gemini",
            gemini_model=os.getenv("GEMINI_EMBEDDING_MODEL", "models/embedding-001"),
            gemini_api_key=os.getenv("GEMINI_API_KEY")
        )
        
        output_path = os.getenv(
            "EMBEDDING_ALIGNMENT_MATRIX_PATH_GEMINI",
            "alignment_matrix_gemini.npy"
        )
        
        alignment_matrix = embedder.calibrate_models(SAMPLE_TEXTS, output_path)
        logger.info(f"✅ Gemini calibration complete: {alignment_matrix.shape}")
        
        return alignment_matrix
    except Exception as e:
        logger.error(f"❌ Gemini calibration failed: {e}")
        raise


def calibrate_ollama():
    """Calibrate Ollama/Qwen embeddings to local model space."""
    logger.info("Calibrating Ollama/Qwen embeddings...")
    
    try:
        embedder = HealthcareHybridEmbedder(
            local_model_name="all-MiniLM-L12-v2",
            query_embedder_type="ollama",
            qwen_model=os.getenv("OLLAMA_MODEL", "qwen3:14b"),
            ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        )
        
        output_path = os.getenv(
            "EMBEDDING_ALIGNMENT_MATRIX_PATH_OLLAMA",
            "alignment_matrix_ollama.npy"
        )
        
        alignment_matrix = embedder.calibrate_models(SAMPLE_TEXTS, output_path)
        logger.info(f"✅ Ollama calibration complete: {alignment_matrix.shape}")
        
        return alignment_matrix
    except Exception as e:
        logger.error(f"❌ Ollama calibration failed: {e}")
        raise


def main():
    """Run calibration for all embedder types."""
    load_dotenv()
    
    logger.info("=" * 60)
    logger.info("Starting embedding calibration...")
    logger.info(f"Using {len(SAMPLE_TEXTS)} sample texts")
    logger.info("=" * 60)
    
    results = {}
    
    # Calibrate Gemini
    if os.getenv("GEMINI_API_KEY"):
        logger.info("\n📊 Calibrating Gemini...")
        try:
            results["gemini"] = calibrate_gemini()
        except Exception as e:
            logger.error(f"Gemini calibration failed: {e}")
            results["gemini"] = None
    else:
        logger.warning("⚠️  GEMINI_API_KEY not set, skipping Gemini calibration")
        results["gemini"] = None
    
    # Calibrate Ollama
    logger.info("\n📊 Calibrating Ollama...")
    try:
        results["ollama"] = calibrate_ollama()
    except Exception as e:
        logger.error(f"Ollama calibration failed: {e}")
        results["ollama"] = None
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("Calibration Summary:")
    logger.info("=" * 60)
    
    if results.get("gemini") is not None:
        logger.info(f"✅ Gemini: {results['gemini'].shape}")
    else:
        logger.info("❌ Gemini: Failed or skipped")
    
    if results.get("ollama") is not None:
        logger.info(f"✅ Ollama: {results['ollama'].shape}")
    else:
        logger.info("❌ Ollama: Failed or skipped")
    
    logger.info("\n✅ Calibration complete!")
    logger.info("\nNext steps:")
    logger.info("1. Verify calibration matrices were created")
    logger.info("2. Test queries with both embedder types")
    logger.info("3. Monitor retrieval quality improvements")


if __name__ == "__main__":
    main()

