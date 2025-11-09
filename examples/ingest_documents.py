"""
Example script for ingesting documents into the architecture pattern knowledge base.
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
    """Example: Ingest documents into the knowledge base."""
    
    # Initialize orchestrator
    orchestrator = DocumentStoreOrchestrator(
        persist_directory="./data/chroma_db",
        collection_name="architecture_patterns",
    )
    
    # Example: Ingest documentation files
    # Replace with your actual document paths
    document_sources = [
        # "./docs/patterns/basic-rag.md",
        # "./docs/patterns/advanced-rag.md",
        # "./specs/001-ai-summarization-reference-architecture/spec.md",
    ]
    
    if document_sources:
        logger.info("Ingesting documents...")
        count = orchestrator.ingest_documents(document_sources)
        logger.info(f"Successfully ingested {count} documents")
    else:
        logger.info("No documents specified. Update document_sources list with your document paths.")
    
    # Get store info
    info = orchestrator.get_store_info()
    logger.info(f"Document store info: {info}")


if __name__ == "__main__":
    main()

