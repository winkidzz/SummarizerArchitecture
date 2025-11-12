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

    "CSV FORMATTING RULES (CRITICAL):\n"
    "- ALWAYS enclose fields containing commas in double quotes\n"
    "- ALWAYS enclose fields containing double quotes in double quotes (and escape internal quotes)\n"
    "- ALWAYS enclose fields containing newlines in double quotes\n"
    "- Example: \"patterns, distributions, and relationships\" (quoted because of commas)\n"
    "- Example: \"CRISP-DM, KDD Process\" (quoted because of comma)\n"
    "- Example: \"Analyze data (FHIR, EHR, BigQuery)\" (quoted because of commas in parentheses)\n"
    "- Strip markdown formatting (**, *, etc.) from cell values\n"
    "- Each row must have exactly the same number of fields as the header\n"
    "- Test your CSV by counting commas: header should have N-1 commas, each data row should have N-1 commas (where N = number of columns)\n\n"

    "COMPLETE DOCUMENTS AND TABLES:\n"
    "- When users request 'complete', 'entire', 'full', or 'all' content from a specific document, "
    "use the get_complete_document() tool instead of query_architecture_patterns().\n"
    "- The get_complete_document() tool retrieves ALL chunks from a document in sequential order "
    "and automatically reconstructs the complete content.\n"
    "- Example queries that should use get_complete_document():\n"
    "  * 'Show me the complete techniques catalog'\n"
    "  * 'Give me the entire table from ai-development-techniques'\n"
    "  * 'List all techniques from the framework document'\n"
    "- Pass a partial document name (e.g., 'ai-development-techniques') to source_filter.\n"
    "- The tool returns reconstructed content with deduplicated headers - use it directly.\n\n"

    "MULTI-CHUNK TABLE HANDLING:\n"
    "- If using query_architecture_patterns() returns table chunks, check metadata for chunk_index.\n"
    "- If chunks have chunk_index metadata, sort them by chunk_index before processing.\n"
    "- Table chunks now include headers, so you can process each chunk independently.\n"
    "- For large tables, consider using get_complete_document() instead of similarity search.\n\n"

    "LARGE DATASETS: For comprehensive queries about specific topics (not complete documents), "
    "use n_results=20-30 to retrieve multiple relevant chunks, then aggregate them "
    "into a complete formatted response."
)


def setup_sys_path() -> Path:
    """
    Setup sys.path to include repository root and src directory.
    Returns the repository root path.

    File location: pattern-query-app/.adk/agents/_shared/agent_base.py
    parents[0] = _shared/
    parents[1] = agents/
    parents[2] = .adk/
    parents[3] = pattern-query-app/ <- This is the repo root we need
    """
    # Get repository root (pattern-query-app directory)
    repo_root = Path(__file__).resolve().parents[3]
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


def get_complete_document(source_filter: str) -> Dict[str, Any]:
    """
    Retrieve ALL chunks from a specific document and reconstruct it sequentially.

    This is useful when the user requests a "complete" document, "entire" table,
    or "full catalog" - situations where similarity search would fragment the results.

    Args:
        source_filter: Partial or complete source path to match (e.g.,
                      "ai-development-techniques", "framework/ai-development-techniques.md")

    Returns:
        Dictionary with:
        - success: bool
        - source: matched source path
        - chunks: list of chunks sorted by chunk_index
        - content: reconstructed full content
        - total_chunks: number of chunks
        - error: error message if failed
    """
    try:
        vector_store = get_vector_store()
        collection = vector_store.collection

        # Get ALL documents from collection (no where clause - not supported in get())
        all_results = collection.get(
            include=["metadatas", "documents"],
        )

        if not all_results or not all_results.get("documents"):
            return {
                "success": False,
                "error": "No documents found in collection",
                "chunks": [],
                "total_chunks": 0,
            }

        # Filter documents that match the source filter (client-side filtering)
        matching_chunks = []
        for doc, metadata in zip(all_results["documents"], all_results["metadatas"]):
            source = metadata.get("source", "")
            if source_filter.lower() in source.lower():
                matching_chunks.append({
                    "content": doc,
                    "metadata": metadata,
                    "chunk_index": metadata.get("chunk_index", 0),
                    "source": source,
                })

        if not matching_chunks:
            return {
                "success": False,
                "error": f"No documents found matching '{source_filter}'",
                "chunks": [],
                "total_chunks": 0,
            }

        # Sort by chunk_index to reconstruct sequential document
        matching_chunks.sort(key=lambda x: x["chunk_index"])

        # Get the actual source path from first chunk
        source_path = matching_chunks[0]["source"] if matching_chunks else ""

        # Reconstruct full content by joining all chunks
        # For tables, we need to deduplicate headers
        full_content = ""
        seen_header = None

        for chunk in matching_chunks:
            content = chunk["content"]

            # Detect and skip duplicate table headers (except first occurrence)
            lines = content.split("\n")
            if len(lines) >= 2 and lines[0].strip().startswith("|") and lines[1].strip().startswith("|---"):
                # This chunk has a header
                header = lines[0] + "\n" + lines[1]
                if seen_header is None:
                    # First header, keep it
                    seen_header = header
                    full_content += content + "\n"
                else:
                    # Skip duplicate header, only add content after header
                    content_after_header = "\n".join(lines[2:])
                    full_content += content_after_header + "\n"
            else:
                # No header in this chunk, add as-is
                full_content += content + "\n"

        return {
            "success": True,
            "source": source_path,
            "chunks": matching_chunks,
            "content": full_content.strip(),
            "total_chunks": len(matching_chunks),
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Error retrieving document: {str(e)}",
            "chunks": [],
            "total_chunks": 0,
        }
