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

    # Collect all markdown files
    docs_dir = REPO_ROOT / "docs"

    pattern_paths = []
    if (docs_dir / "patterns").exists():
        pattern_paths.extend(list((docs_dir / "patterns").glob("*.md")))

    if (docs_dir / "ai-design-patterns").exists():
        pattern_paths.extend(list((docs_dir / "ai-design-patterns").rglob("*.md")))

    if (docs_dir / "vendor-guides").exists():
        pattern_paths.extend(list((docs_dir / "vendor-guides").glob("*.md")))

    if (docs_dir / "use-cases").exists():
        pattern_paths.extend(list((docs_dir / "use-cases").glob("*.md")))

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

            # Extract title from first heading or filename
            title = doc_path.stem.replace("-", " ").title()
            lines = content.split("\n")
            for line in lines[:10]:
                if line.startswith("# "):
                    title = line.lstrip("# ").strip()
                    break

            documents_to_add.append({
                "content": content,
                "metadata": {
                    "source": str(doc_path.relative_to(REPO_ROOT)),
                    "title": title,
                    "type": doc_type,
                    "filename": doc_path.name,
                }
            })
            logger.info(f"  ✓ Processed: {doc_path.name}")
        else:
            logger.warning(f"  ⚠ Skipped (too short): {doc_path.name}")

    # Add to vector store
    if documents_to_add:
        logger.info(f"\nAdding {len(documents_to_add)} documents to vector store...")
        vector_store.add_documents(documents_to_add)

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
