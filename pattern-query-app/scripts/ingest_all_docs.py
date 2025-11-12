#!/usr/bin/env python3
"""
Simple script to ingest all documentation into ChromaDB.
"""

import sys
from pathlib import Path

# Add src to path
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from document_store.storage.vector_store import VectorStore
from document_store.processors.text_chunker import TextChunker
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def read_markdown(file_path: Path) -> str:
    """Read markdown file content."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading {file_path}: {e}")
        return ""


def main():
    """Ingest all documentation files into ChromaDB."""

    # Initialize vector store
    logger.info("Initializing vector store...")
    vector_store = VectorStore(
        persist_directory=str(REPO_ROOT / "data" / "chroma_db"),
        collection_name="architecture_patterns",
    )
    
    # Initialize chunker for large documents
    chunker = TextChunker(
        chunk_size=2000,  # 2000 characters per chunk
        chunk_overlap=200,  # 200 character overlap
    )

    # Collect all markdown files from the pattern library
    pattern_lib_dir = REPO_ROOT.parent / "pattern-library"

    pattern_paths = []
    # RAG patterns
    if (pattern_lib_dir / "patterns" / "rag").exists():
        pattern_paths.extend(list((pattern_lib_dir / "patterns" / "rag").glob("*.md")))

    # AI design patterns
    if (pattern_lib_dir / "patterns" / "ai-design").exists():
        pattern_paths.extend(list((pattern_lib_dir / "patterns" / "ai-design").rglob("*.md")))

    # Vendor guides
    if (pattern_lib_dir / "vendor-guides").exists():
        pattern_paths.extend(list((pattern_lib_dir / "vendor-guides").glob("*.md")))

    # Use cases
    if (pattern_lib_dir / "use-cases").exists():
        pattern_paths.extend(list((pattern_lib_dir / "use-cases").glob("*.md")))

    # Framework documentation
    if (pattern_lib_dir / "framework").exists():
        pattern_paths.extend(list((pattern_lib_dir / "framework").glob("*.md")))

    logger.info(f"Found {len(pattern_paths)} documents to ingest")

    # Process and add documents
    documents_to_add = []
    for doc_path in pattern_paths:
        content = read_markdown(doc_path)
        if content and len(content) > 100:  # Skip very small files
            # Determine document type
            doc_type = "pattern"
            if "vendor-guides" in str(doc_path):
                doc_type = "vendor-guide"
            elif "use-cases" in str(doc_path):
                doc_type = "use-case"
            elif "ai-design-patterns" in str(doc_path):
                doc_type = "ai-design-pattern"
            elif "framework" in str(doc_path):
                doc_type = "framework"

            # Extract title from first heading or filename
            title = doc_path.stem.replace("-", " ").title()
            lines = content.split("\n")
            for line in lines[:10]:
                if line.startswith("# "):
                    title = line.lstrip("# ").strip()
                    break

            base_metadata = {
                "source": str(doc_path.relative_to(pattern_lib_dir)),
                "title": title,
                "type": doc_type,
                "filename": doc_path.name,
            }
            
            # Chunk large documents (especially those with tables)
            if len(content) > 5000 or "|" in content[:500]:  # Large files or files with tables
                logger.info(f"  📄 Chunking large document: {doc_path.name} ({len(content)} chars)")
                if "|" in content and "\n|" in content:
                    # Use table-aware chunking
                    chunks = chunker.chunk_markdown_table(content, base_metadata)
                else:
                    # Use regular chunking
                    chunks = chunker.chunk_text(content, base_metadata)
                
                documents_to_add.extend(chunks)
                logger.info(f"  ✓ Processed into {len(chunks)} chunks: {doc_path.name}")
            else:
                # Small document, add as-is
                documents_to_add.append({
                    "content": content,
                    "metadata": base_metadata,
                })
                logger.info(f"  ✓ Processed: {doc_path.name}")
        else:
            logger.warning(f"  ⚠ Skipped (too short): {doc_path.name}")

    # Add to vector store
    if documents_to_add:
        logger.info(f"\nAdding {len(documents_to_add)} documents to vector store...")
        
        # Generate unique IDs for chunks
        ids = []
        for i, doc in enumerate(documents_to_add):
            metadata = doc.get("metadata", {})
            source = metadata.get("source", f"doc_{i}")
            chunk_index = metadata.get("chunk_index")
            
            if chunk_index is not None:
                # Chunked document - include chunk index in ID
                ids.append(f"{source}__chunk_{chunk_index}")
            else:
                # Regular document
                ids.append(source)
        
        vector_store.add_documents(documents_to_add, ids=ids)

        # Verify
        info = vector_store.get_collection_info()
        logger.info(f"\n{'='*70}")
        logger.info(f"✅ Ingestion complete!")
        logger.info(f"✅ Total documents in store: {info['document_count']}")
        logger.info(f"✅ Collection: {info['collection_name']}")
        logger.info(f"✅ Path: {info['persist_directory']}")
        logger.info(f"{'='*70}")
    else:
        logger.error("No documents to add!")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
