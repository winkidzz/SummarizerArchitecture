#!/usr/bin/env python3
"""
Simple CLI to query patterns using local Ollama models (Gemma3:4b).
Works without any API keys - 100% local.
"""

import sys
from pathlib import Path

# Add src to path
REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(SRC_DIR))

from document_store.orchestrator import DocumentStoreOrchestrator
import os

def main():
    """Interactive query interface using Ollama."""

    # Use Gemma3:4b (Google's open-source model running locally)
    model = os.getenv("OLLAMA_MODEL", "gemma3:4b")

    print(f"\n{'='*70}")
    print(f"🤖 Pattern Query - Local Ollama ({model})")
    print(f"{'='*70}\n")
    print("💻 100% Local - No API Keys Required")
    print("📚 Querying ChromaDB Architecture Patterns\n")
    print(f"Using model: {model}")
    print("Type 'quit' or 'exit' to stop\n")

    # Initialize orchestrator with Ollama
    try:
        orchestrator = DocumentStoreOrchestrator(
            persist_directory="data/chroma_db",
            collection_name="architecture_patterns",
            use_adk_agent=False,  # Don't use ADK (requires Google API)
            ollama_model=model,    # Use local Ollama model
        )
        print("✓ Connected to ChromaDB and Ollama\n")
    except Exception as e:
        print(f"✗ Error initializing: {e}")
        print("\nMake sure Ollama is running and the model is available.")
        print(f"  ollama list  # Check available models")
        print(f"  ollama pull {model}  # Pull the model if needed")
        return 1

    # Interactive loop
    while True:
        try:
            query = input("🔍 Your question: ").strip()

            if query.lower() in ['quit', 'exit', 'q']:
                print("\nGoodbye!")
                break

            if not query:
                continue

            print(f"\n⏳ Querying with {model}...\n")

            # Query using Ollama RAG
            result = orchestrator.query_patterns(
                query=query,
                n_results=5,
                use_agent=False,
                use_ollama_rag=True,  # Use Ollama for response generation
            )

            # Display results
            if 'response' in result:
                print(f"🤖 Response:\n{result['response']}\n")

            if 'results' in result:
                print(f"📚 Retrieved {len(result['results'])} relevant documents\n")

            print(f"{'-'*70}\n")

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\n✗ Error: {e}\n")
            continue

if __name__ == "__main__":
    sys.exit(main() or 0)
