"""
Google ADK agent using local Ollama models.

This agent uses Ollama's OpenAI-compatible API to run models locally,
eliminating the need for cloud API keys while querying the architecture patterns.
"""

from __future__ import annotations

import os
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional

from google.adk import Agent
from google.adk.tools import FunctionTool
from google.adk.models.lite_llm import LiteLlm

# Ensure the repository root and src directory are importable when ADK loads the agent package.
REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_DIR = REPO_ROOT / "src"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# Import only the components we need to avoid circular imports
from document_store.storage.vector_store import VectorStore
from document_store.search.rag_query import RAGQueryInterface

DEFAULT_PERSIST_PATH = "data/chroma_db"
DEFAULT_PERSIST_IS_ABSOLUTE = False
DEFAULT_COLLECTION_NAME = "architecture_patterns"

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

# Ollama configuration
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3:14b")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
AGENT_NAME = os.getenv("ADK_AGENT_NAME", "ollama_pattern_agent")

DEFAULT_INSTRUCTION = (
    "You are the reference librarian for the AI Summarization Reference "
    "Architecture. Use the available tools to search the local ChromaDB store "
    "for patterns, specifications, and healthcare use-case guidance. Always "
    "cite the `id` field (or metadata source) from tool responses when "
    "answering. If a question cannot be answered from the knowledge base, say "
    "so explicitly."
)


@lru_cache(maxsize=1)
def _get_vector_store() -> VectorStore:
    """Build a lightweight vector store for direct ChromaDB access."""
    return VectorStore(
        persist_directory=PERSIST_DIRECTORY,
        collection_name=COLLECTION_NAME,
        embedding_model=EMBEDDING_MODEL,
    )


@lru_cache(maxsize=1)
def _get_rag_interface() -> RAGQueryInterface:
    """Build RAG interface for querying patterns."""
    return RAGQueryInterface(_get_vector_store())


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
    rag_interface = _get_rag_interface()
    return rag_interface.query_patterns(
        query=query,
        n_results=n_results,
        pattern_type=pattern_type,
        vendor=vendor,
    )


def get_store_info() -> Dict[str, Any]:
    """Return collection metadata (document counts, persistence path, etc.)."""
    vector_store = _get_vector_store()
    return vector_store.get_collection_info()


# Set environment variables for LiteLLM to use Ollama
# LiteLLM uses OPENAI_API_BASE (not OPENAI_BASE_URL) for custom endpoints
os.environ["OPENAI_API_KEY"] = "ollama"  # Ollama doesn't need a real key
os.environ["OPENAI_API_BASE"] = OLLAMA_BASE_URL

# Create LiteLLM instance for Ollama
# LiteLLM supports Ollama via the "openai/" prefix with custom base URL
ollama_llm = LiteLlm(model=f"openai/{OLLAMA_MODEL}")

# Create ADK agent using LiteLLM with Ollama
root_agent = Agent(
    name=AGENT_NAME,
    model=ollama_llm,  # Pass LiteLlm instance directly
    instruction=os.getenv("ADK_INSTRUCTION", DEFAULT_INSTRUCTION),
    description=(
        "Answers architecture-pattern and healthcare summarization questions "
        "by retrieving content from the embedded ChromaDB vector store using "
        f"local Ollama model ({OLLAMA_MODEL} via {OLLAMA_BASE_URL})."
    ),
    tools=[
        FunctionTool(query_architecture_patterns),
        FunctionTool(get_store_info),
    ],
)

__all__ = ["root_agent"]
