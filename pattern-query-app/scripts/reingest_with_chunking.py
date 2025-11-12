#!/usr/bin/env python3
"""
Re-ingest documents with proper chunking, especially for large files with tables.
This script will remove old single-chunk documents and re-ingest them as properly chunked documents.
"""

import sys
import argparse
from pathlib import Path

# Add src to path
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from document_store.storage.vector_store import VectorStore
from document_store.processors.text_chunker import TextChunker
import chromadb
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def main():
    """Re-ingest documents with chunking."""
    parser = argparse.ArgumentParser(description="Re-ingest documents with proper chunking")
    parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation prompt")
    args = parser.parse_args()
    
    # Initialize vector store
    logger.info("Initializing vector store...")
    vector_store = VectorStore(
        persist_directory=str(REPO_ROOT / "data" / "chroma_db"),
        collection_name="architecture_patterns",
    )
    
    # Initialize chunker
    chunker = TextChunker(
        chunk_size=2000,
        chunk_overlap=200,
    )
    
    # Get all documents from the vector store's collection
    collection = vector_store.collection
    all_docs = collection.get()
    
    # Find large documents that should be chunked (especially ai-development-techniques.md)
    pattern_lib_dir = REPO_ROOT.parent / "pattern-library"
    files_to_reingest = []
    
    for doc_id, metadata, content in zip(all_docs['ids'], all_docs['metadatas'], all_docs['documents']):
        filename = metadata.get('filename', '')
        source = metadata.get('source', '')
        
        # Check if this is a large file that should be chunked
        if len(content) > 5000:
            # Check if it's already chunked
            is_chunked = metadata.get('chunk_index') is not None or '__chunk_' in doc_id
            
            if not is_chunked:
                # This needs to be re-ingested with chunking
                file_path = pattern_lib_dir / source
                if file_path.exists():
                    files_to_reingest.append((doc_id, file_path, metadata))
                    logger.info(f"  📋 Will re-ingest: {filename} ({len(content)} chars, currently 1 chunk)")
    
    if not files_to_reingest:
        logger.info("✅ No files need re-ingestion. All large files are already chunked.")
        return 0
    
    logger.info(f"\nFound {len(files_to_reingest)} files to re-ingest with chunking:")
    for _, file_path, _ in files_to_reingest:
        logger.info(f"  - {file_path.name}")
    
    # Ask for confirmation (unless --yes flag is used)
    if not args.yes:
        response = input("\nProceed with re-ingestion? This will delete old chunks and create new ones. (y/N): ")
        if response.lower() != 'y':
            logger.info("Cancelled.")
            return 0
    else:
        logger.info("\nProceeding with re-ingestion (--yes flag provided)...")
    
    # Re-ingest each file
    for doc_id, file_path, old_metadata in files_to_reingest:
        logger.info(f"\n{'='*70}")
        logger.info(f"Re-ingesting: {file_path.name}")
        logger.info(f"{'='*70}")
        
        # Read file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
            continue
        
        # Determine document type
        doc_type = old_metadata.get('type', 'pattern')
        if "framework" in str(file_path):
            doc_type = "framework"
        
        # Extract title
        title = old_metadata.get('title', file_path.stem.replace("-", " ").title())
        lines = content.split("\n")
        for line in lines[:10]:
            if line.startswith("# "):
                title = line.lstrip("# ").strip()
                break
        
        base_metadata = {
            "source": str(file_path.relative_to(pattern_lib_dir)),
            "title": title,
            "type": doc_type,
            "filename": file_path.name,
        }
        
        # Chunk the document
        if "|" in content and "\n|" in content:
            logger.info(f"  📄 Using table-aware chunking...")
            chunks = chunker.chunk_markdown_table(content, base_metadata)
        else:
            logger.info(f"  📄 Using regular chunking...")
            chunks = chunker.chunk_text(content, base_metadata)
        
        logger.info(f"  ✓ Created {len(chunks)} chunks")
        
        # Delete old document(s)
        # Find all chunks with this source (in case there are multiple)
        source_to_delete = base_metadata['source']
        docs_to_delete = [
            d_id for d_id, m in zip(all_docs['ids'], all_docs['metadatas'])
            if m.get('source') == source_to_delete and m.get('chunk_index') is None
        ]
        
        if docs_to_delete:
            logger.info(f"  🗑️  Deleting {len(docs_to_delete)} old document(s)...")
            collection.delete(ids=docs_to_delete)
        
        # Add new chunks
        ids = [f"{base_metadata['source']}__chunk_{chunk['metadata']['chunk_index']}" for chunk in chunks]
        documents = [{"content": chunk["content"], "metadata": chunk["metadata"]} for chunk in chunks]
        
        vector_store.add_documents(documents, ids=ids)
        logger.info(f"  ✅ Added {len(chunks)} new chunks")
    
    # Verify
    info = vector_store.get_collection_info()
    logger.info(f"\n{'='*70}")
    logger.info(f"✅ Re-ingestion complete!")
    logger.info(f"✅ Total documents in store: {info['document_count']}")
    logger.info(f"{'='*70}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

