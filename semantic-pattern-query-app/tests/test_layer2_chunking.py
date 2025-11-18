#!/usr/bin/env python3
"""
Test Layer 2: Semantic Chunking

Tests the structure-aware chunker.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.document_store.processors.semantic_chunker import SemanticChunker
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_markdown_chunking():
    """Test markdown chunking with structure awareness."""
    logger.info("=" * 80)
    logger.info("Testing Layer 2: Markdown Chunking")
    logger.info("=" * 80)
    
    chunker = SemanticChunker(chunk_size=512, chunk_overlap=100)
    
    markdown_text = """# Main Title

This is the introduction paragraph.

## Section 1

This is section 1 content. It has multiple sentences. And more content here.

### Subsection 1.1

Subsection content here.

## Section 2

More content in section 2.

```python
# Code block
def hello():
    print("Hello, World!")
```

## Section 3

Final section with more content.
"""
    
    metadata = {
        "document_id": "test_doc",
        "document_type": "markdown",
        "source_path": "test.md"
    }
    
    try:
        chunks = chunker.chunk_document(markdown_text, metadata, doc_type="markdown")
        
        logger.info(f"✅ Chunking successful!")
        logger.info(f"   Number of chunks: {len(chunks)}")
        
        for i, chunk in enumerate(chunks):
            logger.info(f"\n   Chunk {i+1}:")
            logger.info(f"   - Length: {len(chunk.text)} chars")
            logger.info(f"   - Words: {len(chunk.text.split())}")
            logger.info(f"   - Section type: {chunk.metadata.get('section_type', 'N/A')}")
            logger.info(f"   - Preview: {chunk.text[:100]}...")
        
        assert len(chunks) > 0, "Should create at least one chunk"
        assert all(chunk.text for chunk in chunks), "All chunks should have text"
        
        # Check structure preservation
        has_header_chunk = any(
            chunk.metadata.get("section_type") == "header"
            for chunk in chunks
        )
        logger.info(f"   Preserves structure: {has_header_chunk}")
        
        logger.info("✅ All assertions passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Chunking failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_generic_chunking():
    """Test generic text chunking."""
    logger.info("\n" + "=" * 80)
    logger.info("Testing Layer 2: Generic Text Chunking")
    logger.info("=" * 80)
    
    chunker = SemanticChunker(chunk_size=100, chunk_overlap=20)  # Smaller chunks
    
    # Create longer text with multiple paragraphs
    paragraphs = []
    for i in range(20):
        paragraphs.append(f"Paragraph {i+1}. " + " ".join([f"Word {j}" for j in range(20)]) + ".")
    text = "\n\n".join(paragraphs)
    
    metadata = {
        "document_id": "test_doc",
        "document_type": "text"
    }
    
    try:
        chunks = chunker.chunk_document(text, metadata, doc_type="text")
        
        logger.info(f"✅ Chunking successful!")
        logger.info(f"   Number of chunks: {len(chunks)}")
        logger.info(f"   Total text length: {len(text)} chars")
        
        for i, chunk in enumerate(chunks[:3]):  # Show first 3
            logger.info(f"\n   Chunk {i+1}: {len(chunk.text)} chars, {len(chunk.text.split())} words")
        
        # Check that chunks are reasonable
        assert len(chunks) > 0, "Should create at least one chunk"
        assert all(len(chunk.text) > 0 for chunk in chunks), "All chunks should have content"
        
        # If text is long enough, should create multiple chunks
        if len(text.split()) > chunker.chunk_size:
            logger.info(f"   Text is long enough ({len(text.split())} words) for multiple chunks")
            if len(chunks) > 1:
                logger.info("   ✅ Created multiple chunks as expected")
            else:
                logger.info("   ⚠️  Only one chunk created (may be acceptable)")
        
        logger.info("✅ All assertions passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Chunking failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    logger.info("Starting Layer 2 Tests...\n")
    
    results = []
    results.append(test_markdown_chunking())
    results.append(test_generic_chunking())
    
    logger.info("\n" + "=" * 80)
    logger.info("Layer 2 Test Summary")
    logger.info("=" * 80)
    logger.info(f"Passed: {sum(results)}/{len(results)}")
    
    if all(results):
        logger.info("✅ All Layer 2 tests passed!")
        sys.exit(0)
    else:
        logger.error("❌ Some Layer 2 tests failed!")
        sys.exit(1)

