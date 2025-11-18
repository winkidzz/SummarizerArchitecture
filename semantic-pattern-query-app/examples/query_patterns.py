"""
Example usage of the Semantic Pattern Query App.

This demonstrates how to use the orchestrator to query the pattern library.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.document_store.orchestrator import SemanticPatternOrchestrator


def example_query():
    """Example query function."""
    # Initialize orchestrator
    orchestrator = SemanticPatternOrchestrator()
    
    # Example queries
    queries = [
        "What is RAPTOR RAG?",
        "Explain hybrid retrieval",
        "What are the best practices for RAG in healthcare?",
        "How does semantic chunking work?",
    ]
    
    for query in queries:
        print(f"\n{'='*80}")
        print(f"Query: {query}")
        print('='*80)
        
        result = orchestrator.query(query, top_k=3)
        
        print(f"\nAnswer:\n{result['answer']}")
        print(f"\nSources: {len(result.get('sources', []))}")
        print(f"Cache hit: {result.get('cache_hit', False)}")


if __name__ == "__main__":
    example_query()

