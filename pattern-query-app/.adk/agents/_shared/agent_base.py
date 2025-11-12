"""
Shared base code for all ADK agents.

This module contains common configuration, functions, and tools
that are used by both ollama_agent and gemini_agent.
"""

from __future__ import annotations

import os
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional

# Common configuration
DEFAULT_PERSIST_PATH = "data/chroma_db"
DEFAULT_PERSIST_IS_ABSOLUTE = False
DEFAULT_COLLECTION_NAME = "architecture_patterns"

DEFAULT_INSTRUCTION = (
    "You are the reference librarian for the AI Summarization Reference "
    "Architecture. Use the available tools to search the local ChromaDB store "
    "for patterns, specifications, and healthcare use-case guidance. Always "
    "cite the `id` field (or metadata source) from tool responses when "
    "answering. If a question cannot be answered from the knowledge base, say "
    "so explicitly.\n\n"

    "FORMAT RETRIEVED DATA: When users request specific formats (CSV, JSON, "
    "Markdown tables), format the retrieved data accordingly. 'CSV' means "
    "comma-separated text that can be copied, NOT file creation.\n\n"

    "LARGE DATASETS: For comprehensive queries (e.g., 'complete catalog'), "
    "use n_results=20-30 to retrieve multiple chunks, then aggregate them "
    "into a complete formatted response."
)


def setup_sys_path() -> Path:
    """
    Setup sys.path to include repository root and src directory.
    Returns the repository root path.
    """
    # Get repository root (3 levels up from this file)
    repo_root = Path(__file__).resolve().parents[4]
    src_dir = repo_root / "src"

    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

    return repo_root


# Setup paths and get repo root
REPO_ROOT = setup_sys_path()

# Import after path setup
from document_store.storage.vector_store import VectorStore
from document_store.search.rag_query import RAGQueryInterface

# Calculate persist directory
_default_persist_directory = (
    DEFAULT_PERSIST_PATH
    if DEFAULT_PERSIST_IS_ABSOLUTE
    else str(REPO_ROOT / DEFAULT_PERSIST_PATH)
)

PERSIST_DIRECTORY = os.getenv(
    "ADK_PERSIST_DIRECTORY",
    _default_persist_directory,
)
COLLECTION_NAME = os.getenv("ADK_COLLECTION_NAME", DEFAULT_COLLECTION_NAME)
EMBEDDING_MODEL = os.getenv("ADK_EMBEDDING_MODEL")


@lru_cache(maxsize=1)
def get_vector_store() -> VectorStore:
    """Build a lightweight vector store for direct ChromaDB access."""
    return VectorStore(
        persist_directory=PERSIST_DIRECTORY,
        collection_name=COLLECTION_NAME,
        embedding_model=EMBEDDING_MODEL,
    )


@lru_cache(maxsize=1)
def get_rag_interface() -> RAGQueryInterface:
    """Build RAG interface for querying patterns."""
    return RAGQueryInterface(get_vector_store())


def query_architecture_patterns(
    query: str,
    n_results: int = 5,
    pattern_type: Optional[str] = None,
    vendor: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Search the ChromaDB store for architecture content.

    Args:
        query: Natural-language question or keyword search.
        n_results: Maximum number of vector hits to return.
        pattern_type: Optional filter matching the pattern slug (e.g. basic-rag).
        vendor: Optional vendor filter (gemini, azure, aws, etc.).
    """
    rag_interface = get_rag_interface()
    return rag_interface.query_patterns(
        query=query,
        n_results=n_results,
        pattern_type=pattern_type,
        vendor=vendor,
    )


def get_store_info() -> Dict[str, Any]:
    """Return collection metadata (document counts, persistence path, etc.)."""
    vector_store = get_vector_store()
    return vector_store.get_collection_info()
