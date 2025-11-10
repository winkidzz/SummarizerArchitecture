"""
Example script for querying architecture patterns from the knowledge base.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from document_store.orchestrator import DocumentStoreOrchestrator
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Example: Query architecture patterns."""
    
    # Initialize orchestrator
    orchestrator = DocumentStoreOrchestrator(
        persist_directory="./data/chroma_db",
        collection_name="architecture_patterns",
    )
    
    # Example queries
    queries = [
        "What is basic RAG pattern?",
        "How to implement RAG with Gemini?",
        "What are the differences between basic and advanced RAG?",
    ]
    
    for query in queries:
        logger.info(f"\nQuery: {query}")
        results = orchestrator.query_patterns(query, n_results=3)
        
        logger.info(f"Found {results['count']} results:")
        for i, result in enumerate(results['results'], 1):
            logger.info(f"\n  Result {i}:")
            logger.info(f"    ID: {result['id']}")
            logger.info(f"    Distance: {result['distance']:.4f}")
            logger.info(f"    Metadata: {result['metadata']}")
            logger.info(f"    Content preview: {result['content'][:200]}...")


if __name__ == "__main__":
    main()

