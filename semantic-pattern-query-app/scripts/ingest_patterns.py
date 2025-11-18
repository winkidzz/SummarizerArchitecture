#!/usr/bin/env python3
"""
Ingest pattern library into the RAG system.

This script processes all markdown files from the pattern-library directory
and ingests them into Qdrant and Elasticsearch.
"""

import sys
import os
from pathlib import Path
import logging

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.document_store.orchestrator import SemanticPatternOrchestrator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main ingestion function."""
    # Get pattern library path
    pattern_library_path = os.getenv(
        "PATTERN_LIBRARY_PATH",
        "../pattern-library"
    )
    
    pattern_library = Path(pattern_library_path)
    if not pattern_library.exists():
        logger.error(f"Pattern library not found: {pattern_library_path}")
        logger.error("Set PATTERN_LIBRARY_PATH environment variable or ensure ../pattern-library exists")
        sys.exit(1)
    
    logger.info(f"Ingesting pattern library from: {pattern_library}")
    
    # Initialize orchestrator
    try:
        orchestrator = SemanticPatternOrchestrator()
    except Exception as e:
        logger.error(f"Failed to initialize orchestrator: {e}")
        logger.error("Make sure all services are running:")
        logger.error("  - Qdrant: docker-compose up qdrant")
        logger.error("  - Elasticsearch: docker-compose up elasticsearch")
        logger.error("  - Redis: docker-compose up redis")
        logger.error("  - Ollama: ollama serve")
        sys.exit(1)
    
    # Ingest all markdown files
    try:
        total_chunks = orchestrator.ingest_directory(
            str(pattern_library),
            pattern="**/*.md"
        )
        
        logger.info(f"✅ Successfully ingested {total_chunks} chunks")
        
        # Print stats
        stats = orchestrator.get_stats()
        logger.info(f"📊 Collection stats: {stats['qdrant']['points_count']} points")
        
    except Exception as e:
        logger.error(f"Error during ingestion: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

