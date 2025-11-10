"""
Example script for using web search to find architecture patterns.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from document_store.search.web_search import WebSearchTool
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Example: Search the web for architecture patterns."""
    
    # Initialize web search tool
    web_search = WebSearchTool(backend="duckduckgo")
    
    # Example searches
    queries = [
        "advanced RAG patterns 2024",
        "LangChain RAG implementation",
        "Gemini summarization architecture",
    ]
    
    for query in queries:
        logger.info(f"\nSearching for: {query}")
        results = web_search.search(query, max_results=5)
        
        logger.info(f"Found {len(results)} results:")
        for i, result in enumerate(results, 1):
            logger.info(f"\n  Result {i}:")
            logger.info(f"    Title: {result['title']}")
            logger.info(f"    URL: {result['url']}")
            logger.info(f"    Snippet: {result['snippet'][:150]}...")


if __name__ == "__main__":
    main()

