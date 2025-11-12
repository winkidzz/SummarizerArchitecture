#!/usr/bin/env python3
"""Analyze the quality of table chunking in the vector store."""

import sys
from pathlib import Path

# Add src to path
repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root / "src"))

from document_store.storage.vector_store import VectorStore


def analyze_chunking():
    """Analyze table chunks for ai-development-techniques.md."""
    # Get store info
    store = VectorStore()
    collection = store.collection

    # Get all documents
    results = collection.get(include=['metadatas', 'documents'])

    # Analyze table chunks
    table_chunks = []
    for i, (doc, metadata) in enumerate(zip(results['documents'], results['metadatas'])):
        if metadata.get('is_table_chunk'):
            source = metadata.get('source', '')
            if 'ai-development-techniques' in source:
                table_chunks.append({
                    'chunk_index': metadata.get('chunk_index', 0),
                    'size': len(doc),
                    'has_header': '| Phase |' in doc or '| Category |' in doc,
                    'num_rows': doc.count('|') // 7 if '|' in doc else 0,  # Approx rows
                    'source': source
                })

    # Sort by chunk_index
    table_chunks.sort(key=lambda x: x['chunk_index'])

    print(f'Found {len(table_chunks)} table chunks from ai-development-techniques.md')
    print(f'\nFirst 10 Chunks Analysis:')
    for chunk in table_chunks[:10]:
        print(f"  Chunk {chunk['chunk_index']}: size={chunk['size']}, "
              f"has_header={chunk['has_header']}, rows~{chunk['num_rows']}")

    # Check if headers are preserved
    headers_present = sum(1 for c in table_chunks if c['has_header'])
    print(f'\nChunks with headers: {headers_present}/{len(table_chunks)}')

    if headers_present == len(table_chunks):
        print('SUCCESS: All table chunks have headers!')
    else:
        print(f'ISSUE: {len(table_chunks) - headers_present} chunks missing headers')

    # Analyze chunk sizes
    avg_size = sum(c['size'] for c in table_chunks) / len(table_chunks) if table_chunks else 0
    min_size = min(c['size'] for c in table_chunks) if table_chunks else 0
    max_size = max(c['size'] for c in table_chunks) if table_chunks else 0

    print(f'\nChunk Size Statistics:')
    print(f'  Average: {avg_size:.0f} chars')
    print(f'  Min: {min_size} chars')
    print(f'  Max: {max_size} chars')
    print(f'  Target: 2000 chars (configured chunk_size)')


if __name__ == '__main__':
    analyze_chunking()
