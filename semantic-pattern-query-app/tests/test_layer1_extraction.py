#!/usr/bin/env python3
"""
Test Layer 1: Document Extraction

Tests the robust document extractor with multi-stage fallback.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.document_store.processors.robust_extractor import RobustDocumentExtractor
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_markdown_extraction():
    """Test markdown file extraction."""
    logger.info("=" * 80)
    logger.info("Testing Layer 1: Markdown Extraction")
    logger.info("=" * 80)
    
    extractor = RobustDocumentExtractor()
    
    # Test with a markdown file from pattern-library
    test_file = Path("../pattern-library/README.md")
    if not test_file.exists():
        logger.warning(f"Test file not found: {test_file}")
        logger.info("Creating a test markdown file...")
        test_file = Path("test_sample.md")
        test_file.write_text("""# Test Document

This is a test markdown file.

## Section 1

Some content here.

## Section 2

More content with **bold** and *italic* text.
""")
    
    try:
        result = extractor.extract(str(test_file))
        
        logger.info(f"✅ Extraction successful!")
        logger.info(f"   Method: {result.method}")
        logger.info(f"   Confidence: {result.confidence:.2f}")
        logger.info(f"   Text length: {len(result.text)} characters")
        logger.info(f"   Has tables: {result.has_tables}")
        logger.info(f"   Sample text (first 200 chars):")
        logger.info(f"   {result.text[:200]}...")
        
        assert result.text, "Extracted text should not be empty"
        assert result.confidence > 0.5, "Confidence should be reasonable"
        
        logger.info("✅ All assertions passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Extraction failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_text_extraction():
    """Test plain text file extraction."""
    logger.info("\n" + "=" * 80)
    logger.info("Testing Layer 1: Text Extraction")
    logger.info("=" * 80)
    
    extractor = RobustDocumentExtractor()
    
    # Create a test text file
    test_file = Path("test_sample.txt")
    test_file.write_text("""This is a plain text file.

It has multiple paragraphs.

And some more content here.
""")
    
    try:
        result = extractor.extract(str(test_file))
        
        logger.info(f"✅ Extraction successful!")
        logger.info(f"   Method: {result.method}")
        logger.info(f"   Confidence: {result.confidence:.2f}")
        logger.info(f"   Text length: {len(result.text)} characters")
        
        assert result.text, "Extracted text should not be empty"
        assert result.method == "text", "Should use text extraction method"
        
        logger.info("✅ All assertions passed!")
        
        # Cleanup
        test_file.unlink()
        return True
        
    except Exception as e:
        logger.error(f"❌ Extraction failed: {e}")
        import traceback
        traceback.print_exc()
        if test_file.exists():
            test_file.unlink()
        return False


if __name__ == "__main__":
    logger.info("Starting Layer 1 Tests...\n")
    
    results = []
    results.append(test_markdown_extraction())
    results.append(test_text_extraction())
    
    logger.info("\n" + "=" * 80)
    logger.info("Layer 1 Test Summary")
    logger.info("=" * 80)
    logger.info(f"Passed: {sum(results)}/{len(results)}")
    
    if all(results):
        logger.info("✅ All Layer 1 tests passed!")
        sys.exit(0)
    else:
        logger.error("❌ Some Layer 1 tests failed!")
        sys.exit(1)

