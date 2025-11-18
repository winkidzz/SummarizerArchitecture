#!/usr/bin/env python3
"""
Test All Layers Sequentially

Runs tests for all 7 layers in order.
"""

import sys
from pathlib import Path
import subprocess
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TEST_FILES = [
    "test_layer1_extraction.py",
    "test_layer2_chunking.py",
    "test_layer3_embeddings.py",
    "test_layer4_qdrant.py",
    "test_layer5_hybrid_retrieval.py",
    "test_layer6_generation.py",
    "test_layer7_caching.py",
]


def run_test(test_file: str) -> bool:
    """Run a single test file."""
    test_path = Path(__file__).parent / test_file
    
    if not test_path.exists():
        logger.warning(f"Test file not found: {test_file}")
        return False
    
    logger.info(f"\n{'='*80}")
    logger.info(f"Running: {test_file}")
    logger.info('='*80)
    
    try:
        result = subprocess.run(
            [sys.executable, str(test_path)],
            cwd=Path(__file__).parent,
            capture_output=True,
            text=True
        )
        
        # Print output
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        logger.error(f"Error running {test_file}: {e}")
        return False


def main():
    """Run all layer tests."""
    logger.info("=" * 80)
    logger.info("Testing All Layers - Semantic Pattern Query App")
    logger.info("=" * 80)
    
    results = {}
    
    for test_file in TEST_FILES:
        results[test_file] = run_test(test_file)
    
    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("Test Summary")
    logger.info("=" * 80)
    
    for test_file, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        logger.info(f"{status}: {test_file}")
    
    total_passed = sum(results.values())
    total_tests = len(results)
    
    logger.info(f"\nTotal: {total_passed}/{total_tests} test suites passed")
    
    if all(results.values()):
        logger.info("\n✅ All layer tests passed!")
        return 0
    else:
        logger.error("\n❌ Some layer tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())

