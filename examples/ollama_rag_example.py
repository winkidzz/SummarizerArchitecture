"""
Example script for using Ollama for specialized RAG tasks.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from document_store.agents.ollama_agent import OllamaAgent
from document_store.storage.vector_store import VectorStore
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Example: Use Ollama for specialized RAG tasks."""
    
    # Initialize vector store
    vector_store = VectorStore(
        persist_directory="./data/chroma_db",
        collection_name="architecture_patterns",
    )
    
    # Initialize Ollama agent
    try:
        ollama_agent = OllamaAgent(
            model="llama3",  # or "mistral", "gemma", etc.
            vector_store=vector_store,
        )
        
        # List available models
        logger.info("Available Ollama models:")
        models = ollama_agent.list_available_models()
        for model in models:
            logger.info(f"  - {model}")
        
        # Example: Query with RAG using Ollama
        query = "What is the basic RAG pattern?"
        logger.info(f"\n{'='*60}")
        logger.info(f"Query: {query}")
        logger.info(f"{'='*60}")
        
        results = ollama_agent.query_with_rag(
            query=query,
            n_results=3,
        )
        
        logger.info(f"\nAnswer: {results.get('answer', 'N/A')}")
        logger.info(f"\nModel: {results.get('model', 'N/A')}")
        logger.info(f"Context documents used: {results.get('context_used', 0)}")
        logger.info(f"\nMetadata: {results.get('metadata', {})}")
        
        logger.info(f"\nSources:")
        for i, source in enumerate(results.get('sources', []), 1):
            logger.info(f"\n  Source {i}:")
            logger.info(f"    ID: {source.get('id', 'N/A')}")
            logger.info(f"    Metadata: {source.get('metadata', {})}")
            logger.info(f"    Content preview: {source.get('content', '')[:150]}...")
        
        # Example: Generate embeddings using Ollama
        logger.info(f"\n{'='*60}")
        logger.info("Generating embeddings with Ollama...")
        texts = [
            "Basic RAG pattern uses retrieval and generation",
            "Advanced RAG includes multi-step retrieval",
        ]
        embeddings = ollama_agent.generate_embeddings(texts)
        logger.info(f"Generated {len(embeddings)} embeddings")
        logger.info(f"Embedding dimension: {len(embeddings[0]) if embeddings else 0}")
        
    except ImportError:
        logger.error(
            "Ollama is not installed. Install it with: pip install ollama\n"
            "Also ensure Ollama is running: ollama serve"
        )
    except Exception as e:
        logger.error(f"Error: {e}")


if __name__ == "__main__":
    main()

