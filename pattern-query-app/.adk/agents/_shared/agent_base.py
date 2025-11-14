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

    "TOOL SELECTION GUIDE - WHEN TO USE STRUCTURED OUTPUT:\n"
    "You have access to specialized structured output tools. Use them intelligently:\n\n"

    "USE generate_structured_table() when:\n"
    "- User explicitly requests CSV, TSV, spreadsheet, or tabular format\n"
    "- Query contains: 'as CSV', 'as table', 'in spreadsheet format'\n"
    "- Example: 'List the Complete Techniques Catalog as CSV'\n"
    "- This tool uses LLM to extract structured data with schema validation\n\n"

    "USE generate_structured_list() when:\n"
    "- User requests a list or catalog (but not in table format)\n"
    "- Query contains: 'list all', 'catalog of', 'enumerate'\n"
    "- Example: 'List all RAG patterns'\n\n"

    "USE generate_comparison_matrix() when:\n"
    "- User requests comparisons between multiple entities\n"
    "- Query contains: 'compare', 'vs', 'differences between'\n"
    "- Example: 'Compare Anthropic vs Azure OpenAI'\n\n"

    "DO NOT USE structured output tools for:\n"
    "- Conceptual questions or explanations\n"
    "- General queries about how something works\n"
    "- Single item lookups or descriptions\n"
    "- When user doesn't specify a particular format\n"
    "- Use query_architecture_patterns() or get_complete_document() instead\n\n"

    "FORMAT RETRIEVED DATA: When structured output tools are not appropriate, "
    "you can still format data manually from query results.\n\n"
    
    "STEP-BY-STEP PROCESS FOR 'Complete Techniques Catalog' CSV (CRITICAL - FOLLOW EXACTLY):\n"
    "1. Call get_complete_document(source_filter='ai-development-techniques')\n"
    "2. In the returned content, search for the exact text '## Complete Techniques Catalog'\n"
    "3. Find the markdown table immediately following this heading\n"
    "4. The table header row is: | Phase | Category | Technique/Methodology | Description | Process Framework | Usage in Architecture | Lifecycle Steps |\n"
    "5. Extract ALL 163 data rows from this table (plus the header row = 164 total rows)\n"
    "6. Convert markdown table to CSV:\n"
    "   - Example markdown row: | **1. Ideation & Planning** | Data Analysis | **Exploratory Data Analysis (EDA)** | Initial data exploration... | CRISP-DM, KDD Process | Analyze healthcare data... | 1.1 Requirements Gathering - Technical |\n"
    "   - Convert to CSV: \"1. Ideation & Planning\",\"Data Analysis\",\"Exploratory Data Analysis (EDA)\",\"Initial data exploration...\",\"CRISP-DM, KDD Process\",\"Analyze healthcare data...\",\"1.1 Requirements Gathering - Technical\"\n"
    "   - Remove markdown bold (**text** → text)\n"
    "   - Quote ALL fields that contain commas, quotes, or newlines\n"
    "   - Remove leading/trailing spaces\n"
    "7. Your response MUST start with the CSV header row, then all 163 data rows\n"
    "8. DO NOT add any text before or after the CSV - no explanations, no markdown, no code blocks\n"
    "9. DO NOT summarize, translate, or modify any content - extract the table exactly as it appears\n"
    "10. The output should be 164 lines total: 1 header + 163 data rows\n\n"

    "CSV FORMATTING RULES (CRITICAL):\n"
    "- When user requests CSV, you MUST return ONLY the CSV data - no explanations, no markdown, no code blocks\n"
    "- Start directly with the header row, then all data rows\n"
    "- ALWAYS enclose fields containing commas in double quotes\n"
    "- ALWAYS enclose fields containing double quotes in double quotes (and escape internal quotes)\n"
    "- ALWAYS enclose fields containing newlines in double quotes\n"
    "- Example: \"patterns, distributions, and relationships\" (quoted because of commas)\n"
    "- Example: \"CRISP-DM, KDD Process\" (quoted because of comma)\n"
    "- Example: \"Analyze data (FHIR, EHR, BigQuery)\" (quoted because of commas in parentheses)\n"
    "- Strip markdown formatting (**, *, etc.) from cell values\n"
    "- Each row must have exactly the same number of fields as the header\n"
    "- For 'Complete Techniques Catalog', expect 7 columns: Phase, Category, Technique/Methodology, Description, Process Framework, Usage in Architecture, Lifecycle Steps\n"
    "- Test your CSV by counting commas: header should have 6 commas (7 columns), each data row should have 6 commas\n"
    "- DO NOT include markdown table syntax (|), code fences (```), or explanatory text - ONLY the CSV rows\n\n"

    "COMPLETE DOCUMENTS AND TABLES:\n"
    "- When users request 'complete', 'entire', 'full', 'all', or 'Complete Techniques Catalog', "
    "use the get_complete_document() tool instead of query_architecture_patterns().\n"
    "- The get_complete_document() tool retrieves ALL chunks from a document in sequential order "
    "and automatically reconstructs the complete content.\n"
    "- CRITICAL: For 'Complete Techniques Catalog' queries, ALWAYS use source_filter='ai-development-techniques'\n"
    "- Example queries that should use get_complete_document():\n"
    "  * 'Show me the complete techniques catalog' → use source_filter='ai-development-techniques'\n"
    "  * 'Give me the entire table from ai-development-techniques' → use source_filter='ai-development-techniques'\n"
    "  * 'List all techniques from the framework document' → use source_filter='ai-development-techniques'\n"
    "- The tool returns reconstructed content with deduplicated headers.\n"
    "- CRITICAL FOR 'Complete Techniques Catalog':\n"
    "  1. Search for the table with header containing: 'Phase', 'Category', 'Technique/Methodology', 'Description', 'Process Framework', 'Usage in Architecture', 'Lifecycle Steps'\n"
    "  2. This table has exactly 163 data rows (plus 1 header row = 164 total rows)\n"
    "  3. Extract ONLY this specific table - ignore all other content, summaries, translations, or explanations\n"
    "  4. Convert the markdown table (| columns |) to CSV format\n"
    "  5. Return ONLY the CSV rows - no markdown, no explanations, no other text\n"
    "  6. DO NOT translate, summarize, or modify the content - extract it exactly as it appears\n"
    "  7. The table starts after a heading like '## Complete Techniques Catalog' or similar\n\n"

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
                      Can also be a content description (e.g., "techniques catalog")
                      which will trigger semantic search fallback.

    Returns:
        Dictionary with:
        - success: bool
        - source: matched source path
        - chunks: list of chunks sorted by chunk_index
        - content: reconstructed full content
        - total_chunks: number of chunks
        - error: error message if failed
        - suggestions: list of alternative sources (if search failed)
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
            # FALLBACK: Try semantic search to find relevant document
            # This helps when user provides content description instead of source name
            try:
                rag_interface = get_rag_interface()
                search_results = rag_interface.query_patterns(
                    query=source_filter,
                    n_results=5
                )

                if search_results.get("results"):
                    # Get unique source documents from search results
                    candidate_sources = {}
                    for result in search_results["results"]:
                        source = result.get("metadata", {}).get("source", "")
                        if source and source not in candidate_sources:
                            candidate_sources[source] = result.get("content", "")[:200]

                    if candidate_sources:
                        # Try the most relevant source automatically
                        best_source = list(candidate_sources.keys())[0]

                        # Extract just the filename for matching
                        import os
                        best_source_name = os.path.basename(best_source).replace(".md", "")

                        # Re-run the search with the discovered source
                        for doc, metadata in zip(all_results["documents"], all_results["metadatas"]):
                            source = metadata.get("source", "")
                            if best_source_name.lower() in source.lower():
                                matching_chunks.append({
                                    "content": doc,
                                    "metadata": metadata,
                                    "chunk_index": metadata.get("chunk_index", 0),
                                    "source": source,
                                })

                        if matching_chunks:
                            # Found via semantic search!
                            pass  # Continue with normal processing below
                        else:
                            # Semantic search found candidates but couldn't retrieve full doc
                            return {
                                "success": False,
                                "error": f"No documents found matching '{source_filter}'",
                                "chunks": [],
                                "total_chunks": 0,
                                "suggestions": [
                                    f"{src} - {preview}..."
                                    for src, preview in list(candidate_sources.items())[:3]
                                ],
                                "hint": f"Try using: {best_source_name}"
                            }
            except Exception as search_error:
                # Semantic search failed, return original error
                pass

            # If still no matches after semantic search fallback
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


# ============================================================================
# Structured Output Tools (Optional - LLM decides when to use)
# ============================================================================

def generate_structured_table(
    source_filter: str,
    output_format: str = "csv",
    schema_name: str = "table"
) -> Dict[str, Any]:
    """
    Generate structured table output using LLM with schema validation.

    USE THIS TOOL when the user explicitly requests:
    - A table in CSV, TSV, or structured format
    - "List as CSV", "create a table", "show in spreadsheet format"
    - Any request for tabular data that needs to be structured

    DO NOT USE this tool for:
    - Conceptual questions or explanations
    - General queries about patterns or techniques
    - Requests that don't need structured/tabular output

    This tool retrieves document content and uses an LLM to extract structured
    data according to a schema, then converts to the requested format.

    Args:
        source_filter: Document source to retrieve (e.g., 'ai-development-techniques')
        output_format: Desired format ('csv', 'tsv', 'markdown', 'json', 'html')
        schema_name: Schema to use ('table', 'techniques_catalog', 'list', etc.)

    Returns:
        Dictionary with:
        - success: bool
        - data: Formatted output (CSV text, JSON, etc.)
        - format: Output format used
        - schema_used: Schema name
        - validation: Validation results
        - metadata: Additional info (row count, columns, etc.)

    Example queries that should use this tool:
        - "List the Complete Techniques Catalog as CSV"
        - "Show me all patterns in a table"
        - "Create a spreadsheet of vendor features"
    """
    try:
        # Import the structured output service
        from document_store.formatting import StructuredOutputService, create_service

        # Get complete document
        doc_result = get_complete_document(source_filter)

        if not doc_result.get("success"):
            return {
                "success": False,
                "error": doc_result.get("error", "Failed to retrieve document"),
                "suggestions": doc_result.get("suggestions", [])
            }

        # Create structured output service
        service = create_service()

        # Generate structured output
        # Use a query that helps the LLM understand what to extract
        query = f"Extract all data from this document as a structured {output_format}"

        result = service.generate_structured_output(
            content=doc_result["content"],
            query=query,
            schema_name=schema_name,
            output_format=output_format,
            validate=True
        )

        return result

    except ImportError as e:
        return {
            "success": False,
            "error": f"Structured output module not available: {str(e)}",
            "fallback": "Use get_complete_document() and format manually"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error generating structured output: {str(e)}",
            "error_type": type(e).__name__
        }


def generate_structured_list(
    query: str,
    n_results: int = 10,
    output_format: str = "json"
) -> Dict[str, Any]:
    """
    Generate structured list/catalog from query results.

    USE THIS TOOL when the user requests:
    - A list or catalog of items
    - "List all X", "catalog of Y", "enumerate Z"
    - Results that should be formatted as a structured collection

    DO NOT USE this tool for:
    - Single item lookups
    - Conceptual explanations
    - Comparison queries (use generate_comparison_matrix instead)

    Args:
        query: Search query
        n_results: Number of results to retrieve
        output_format: Desired format ('json', 'csv', 'markdown', 'yaml')

    Returns:
        Dictionary with structured list output

    Example queries:
        - "List all RAG patterns"
        - "Show me a catalog of available techniques"
        - "Enumerate all vendor integrations"
    """
    try:
        from document_store.formatting import StructuredOutputService, create_service

        # Query patterns
        search_results = query_architecture_patterns(
            query=query,
            n_results=n_results
        )

        if not search_results.get("results"):
            return {
                "success": False,
                "error": "No results found for query"
            }

        # Combine results into content
        content = "\n\n".join([
            f"Item {i+1}:\n{result.get('content', '')}"
            for i, result in enumerate(search_results["results"])
        ])

        # Create structured output service
        service = create_service()

        # Generate structured output
        result = service.generate_structured_output(
            content=content,
            query=query,
            schema_name="list",
            output_format=output_format,
            validate=True
        )

        return result

    except ImportError as e:
        return {
            "success": False,
            "error": f"Structured output module not available: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error generating structured list: {str(e)}"
        }


def generate_comparison_matrix(
    entities: str,
    dimensions: str = "features",
    output_format: str = "markdown"
) -> Dict[str, Any]:
    """
    Generate structured comparison matrix.

    USE THIS TOOL when the user requests:
    - Comparisons between multiple items
    - "Compare X vs Y", "what are the differences between A and B"
    - Feature comparison matrices
    - Vendor/pattern/technique comparisons

    DO NOT USE this tool for:
    - Single item descriptions
    - Simple lists or catalogs
    - Explanations without comparison

    Args:
        entities: Entities to compare (comma-separated or descriptive)
                 e.g., "Anthropic, Google, Azure" or "all cloud vendors"
        dimensions: What to compare (e.g., "features", "pricing", "performance")
        output_format: Desired format ('markdown', 'csv', 'html', 'json')

    Returns:
        Dictionary with comparison matrix output

    Example queries:
        - "Compare Anthropic vs Azure OpenAI"
        - "What are the differences between Basic RAG and Contextual Retrieval?"
        - "Create a feature comparison matrix for all vendors"
    """
    try:
        from document_store.formatting import StructuredOutputService, create_service

        # Build query for comparison
        query = f"Compare {entities} across {dimensions}"

        # Query patterns with more results to get comprehensive data
        search_results = query_architecture_patterns(
            query=query,
            n_results=15
        )

        if not search_results.get("results"):
            return {
                "success": False,
                "error": f"No results found for comparison: {entities}"
            }

        # Combine results into content
        content = "\n\n".join([
            f"{result.get('metadata', {}).get('source', 'Unknown')}:\n{result.get('content', '')}"
            for result in search_results["results"]
        ])

        # Create structured output service
        service = create_service()

        # Generate structured comparison
        result = service.generate_structured_output(
            content=content,
            query=query,
            schema_name="comparison",
            output_format=output_format,
            validate=True
        )

        return result

    except ImportError as e:
        return {
            "success": False,
            "error": f"Structured output module not available: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error generating comparison matrix: {str(e)}"
        }
