#!/usr/bin/env python3
"""
Test script to verify ADK setup and ChromaDB integration.

This script checks:
1. ChromaDB is populated with patterns
2. Vector store queries work
3. ADK agent can be imported and initialized
4. Environment is configured correctly
"""

import os
import sys
from pathlib import Path

# Add repo root and src to path
REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(SRC_DIR))

def test_chromadb_populated():
    """Test that ChromaDB has data."""
    print("\n" + "="*60)
    print("TEST 1: ChromaDB Data Population")
    print("="*60)

    try:
        # Import directly to avoid triggering docling imports
        import sys
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "vector_store",
            SRC_DIR / "document_store" / "storage" / "vector_store.py"
        )
        vector_store_module = importlib.util.module_from_spec(spec)
        sys.modules["vector_store"] = vector_store_module
        spec.loader.exec_module(vector_store_module)
        VectorStore = vector_store_module.VectorStore

        vector_store = VectorStore(
            persist_directory="data/chroma_db",
            collection_name="architecture_patterns"
        )

        info = vector_store.get_collection_info()
        count = info.get("document_count", 0)

        print(f"✓ ChromaDB connected successfully")
        print(f"  - Collection: {info.get('collection_name')}")
        print(f"  - Document count: {count}")
        print(f"  - Persist directory: {info.get('persist_directory')}")

        if count == 0:
            print("\n⚠ WARNING: ChromaDB is empty!")
            print("  Run: python scripts/initialize_and_test.py")
            return False
        else:
            print(f"\n✓ ChromaDB has {count} documents")
            return True

    except Exception as e:
        print(f"✗ Error accessing ChromaDB: {e}")
        return False


def test_vector_query():
    """Test that vector queries work."""
    print("\n" + "="*60)
    print("TEST 2: Vector Store Query")
    print("="*60)

    try:
        from document_store.storage.vector_store import VectorStore
        from document_store.search.rag_query import RAGQueryInterface

        vector_store = VectorStore(
            persist_directory="data/chroma_db",
            collection_name="architecture_patterns"
        )

        rag_interface = RAGQueryInterface(vector_store)

        # Test query
        results = rag_interface.query_patterns(
            query="What is RAG?",
            n_results=3
        )

        print(f"✓ Query executed successfully")
        print(f"  - Query: 'What is RAG?'")
        print(f"  - Results returned: {len(results.get('results', []))}")

        if results.get('results'):
            print("\n  Sample result:")
            first_result = results['results'][0]
            print(f"    - ID: {first_result.get('id', 'N/A')}")
            print(f"    - Distance: {first_result.get('distance', 'N/A'):.4f}")
            content_preview = first_result.get('content', '')[:100]
            print(f"    - Content: {content_preview}...")

        return True

    except Exception as e:
        print(f"✗ Error executing query: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_adk_agent_import():
    """Test that ADK agent can be imported."""
    print("\n" + "="*60)
    print("TEST 3: ADK Agent Import")
    print("="*60)

    try:
        # Check if google-adk is installed
        import google.adk
        print(f"✓ google-adk package found: {google.adk.__version__ if hasattr(google.adk, '__version__') else 'version unknown'}")
    except ImportError:
        print("✗ google-adk not installed")
        print("  Run: pip install google-adk>=1.18.0")
        return False

    try:
        # Try importing the generated agent
        sys.path.insert(0, str(REPO_ROOT / ".adk" / "agents"))
        from chromadb_agent import agent

        print(f"✓ ADK agent imported successfully")
        print(f"  - Agent name: {agent.root_agent.name}")
        print(f"  - Model: {agent.root_agent.model}")
        print(f"  - Tools: {len(agent.root_agent.tools)}")

        for i, tool in enumerate(agent.root_agent.tools, 1):
            tool_name = getattr(tool, 'name', 'unknown')
            print(f"    {i}. {tool_name}")

        return True

    except Exception as e:
        print(f"✗ Error importing ADK agent: {e}")
        print("\n  The agent may need to be regenerated:")
        print("  Run: python scripts/setup_adk_agent.py --overwrite")
        import traceback
        traceback.print_exc()
        return False


def test_environment():
    """Test environment configuration."""
    print("\n" + "="*60)
    print("TEST 4: Environment Configuration")
    print("="*60)

    api_key = os.getenv("GOOGLE_API_KEY")

    if api_key:
        masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
        print(f"✓ GOOGLE_API_KEY is set: {masked_key}")
        return True
    else:
        print("⚠ GOOGLE_API_KEY not set")
        print("  - Get key from: https://aistudio.google.com/app/apikey")
        print("  - Set with: export GOOGLE_API_KEY='your-key-here'")
        print("  - Or add to .env file")
        print("\n  The web UI will not work without this key!")
        return False


def test_adk_cli():
    """Test that ADK CLI is available."""
    print("\n" + "="*60)
    print("TEST 5: ADK CLI Availability")
    print("="*60)

    import subprocess

    try:
        result = subprocess.run(
            ["adk", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            print(f"✓ ADK CLI is available")
            print(f"  Output: {result.stdout.strip() or result.stderr.strip()}")
            return True
        else:
            print(f"⚠ ADK CLI returned error code {result.returncode}")
            return False

    except FileNotFoundError:
        print("✗ ADK CLI not found in PATH")
        print("  - Install: pip install google-adk>=1.18.0")
        print("  - Ensure Python scripts directory is in PATH")
        return False
    except Exception as e:
        print(f"✗ Error checking ADK CLI: {e}")
        return False


def print_next_steps(results):
    """Print next steps based on test results."""
    print("\n" + "="*60)
    print("SUMMARY & NEXT STEPS")
    print("="*60)

    all_passed = all(results.values())

    if all_passed:
        print("\n✓ All tests passed! You're ready to use ADK.\n")
        print("To launch the web UI:")
        print("  ./scripts/start_adk_default_ui.sh")
        print("\nOr use the CLI directly:")
        print("  adk run .adk/agents/chromadb_agent")
        print("\nOr launch the web interface:")
        print("  adk web --host 127.0.0.1 --port 8000 .adk/agents")
        print("\nThen open: http://127.0.0.1:8000")

    else:
        print("\n⚠ Some tests failed. Please fix the issues above.\n")

        if not results.get("chromadb"):
            print("1. Populate ChromaDB:")
            print("   python scripts/initialize_and_test.py")

        if not results.get("adk_import"):
            print("2. Regenerate ADK agent:")
            print("   python scripts/setup_adk_agent.py --overwrite")

        if not results.get("environment"):
            print("3. Set GOOGLE_API_KEY:")
            print("   export GOOGLE_API_KEY='your-key-here'")

        if not results.get("adk_cli"):
            print("4. Install/fix ADK CLI:")
            print("   pip install --upgrade google-adk>=1.18.0")


def main():
    """Run all tests."""
    print("\nADK Setup Verification")
    print("Testing Google ADK integration with ChromaDB pattern store\n")

    results = {
        "chromadb": test_chromadb_populated(),
        "query": test_vector_query(),
        "adk_import": test_adk_agent_import(),
        "environment": test_environment(),
        "adk_cli": test_adk_cli(),
    }

    print_next_steps(results)

    # Return exit code
    sys.exit(0 if all(results.values()) else 1)


if __name__ == "__main__":
    main()
