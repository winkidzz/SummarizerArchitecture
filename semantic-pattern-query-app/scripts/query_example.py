#!/usr/bin/env python3
"""
CLI example for querying the pattern library.

Usage:
    python scripts/query_example.py "What is RAPTOR RAG?"
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
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main query function."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/query_example.py '<query>'")
        print("Example: python scripts/query_example.py 'What is RAPTOR RAG?'")
        sys.exit(1)
    
    query = " ".join(sys.argv[1:])
    
    logger.info(f"Query: {query}")
    
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
    
    try:
        result = orchestrator.query(query, top_k=5)
        
        print("\n" + "="*80)
        print("ANSWER")
        print("="*80)
        print(result["answer"])
        
        if result.get("sources"):
            print("\n" + "="*80)
            print("SOURCES")
            print("="*80)
            for i, source in enumerate(result["sources"], 1):
                print(f"\n[{i}] {source.get('source_path', source.get('document_id', 'Unknown'))}")
                print(f"    Type: {source.get('document_type', 'unknown')}")
        
        print("\n" + "="*80)
        print("METADATA")
        print("="*80)
        print(f"Cache hit: {result.get('cache_hit', False)}")
        print(f"Retrieved docs: {result.get('retrieved_docs', 0)}")
        print(f"Context docs used: {result.get('context_docs_used', 0)}")
        
    except Exception as e:
        logger.error(f"Query error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

