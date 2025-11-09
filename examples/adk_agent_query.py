"""
Example script for using Google ADK Agent Library to query architecture patterns.
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
    """Example: Query patterns using Google ADK Agent."""
    
    # Initialize orchestrator with ADK agent
    orchestrator = DocumentStoreOrchestrator(
        persist_directory="./data/chroma_db",
        collection_name="architecture_patterns",
        use_adk_agent=True,  # Enable ADK agent (primary querying method)
    )
    
    # Example queries using ADK agent
    queries = [
        "What is the basic RAG pattern and when should I use it?",
        "How do I implement RAG with Gemini?",
        "Compare basic RAG vs advanced RAG patterns",
    ]
    
    for query in queries:
        logger.info(f"\n{'='*60}")
        logger.info(f"Query: {query}")
        logger.info(f"{'='*60}")
        
        # Query using ADK agent (primary method)
        results = orchestrator.query_patterns(
            query=query,
            n_results=3,
            use_agent=True,  # Use ADK agent
        )
        
        logger.info(f"\nFound {results.get('count', 0)} results")
        
        # Display results
        if 'results' in results:
            for i, result in enumerate(results['results'], 1):
                logger.info(f"\n  Result {i}:")
                logger.info(f"    ID: {result.get('id', 'N/A')}")
                logger.info(f"    Distance: {result.get('distance', 'N/A')}")
                logger.info(f"    Metadata: {result.get('metadata', {})}")
                logger.info(f"    Content preview: {result.get('content', '')[:200]}...")
        
        # If ADK agent is available, show agent info
        if orchestrator.adk_agent:
            agent_info = orchestrator.adk_agent.get_agent_info()
            logger.info(f"\n  Agent Info: {agent_info}")


if __name__ == "__main__":
    main()

