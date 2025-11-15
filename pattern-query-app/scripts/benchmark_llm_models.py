#!/usr/bin/env python3
"""
Benchmark different LLM models for schema generation and data extraction.

Tests multiple models to compare:
- Speed (latency)
- Quality (output accuracy)
- Two-step performance (schema gen + data extraction)
"""
import sys
import os
import time
import json
from pathlib import Path
from typing import Dict, Any, List

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Set env
os.environ["USE_OLLAMA_EVAL"] = "true"
os.environ["OLLAMA_BASE_URL"] = "http://localhost:11434/v1"

from document_store.formatting import StructuredOutputService

# Test content - realistic but small for fast testing
TEST_CONTENT = """
# RAG Patterns Overview

## Basic RAG
- Description: Simple retrieval augmented generation
- Latency: <500ms
- Throughput: 50 req/s
- Use Case: Simple queries, local testing
- Cost: Low

## Advanced RAG
- Description: Multi-step processing with hybrid retrieval
- Latency: <2000ms
- Throughput: 20 req/s
- Use Case: Production workloads, complex queries
- Cost: Medium

## Self-RAG
- Description: Self-reflective RAG with accuracy validation
- Latency: <3000ms
- Throughput: 10 req/s
- Use Case: Quality-critical applications, healthcare
- Cost: High

## Streaming RAG
- Description: Incremental processing for real-time data
- Latency: <100ms per chunk
- Throughput: 30 req/s
- Use Case: Real-time monitoring, live data
- Cost: Medium
"""

# Models to test (add/remove based on what you have installed)
MODELS_TO_TEST = [
    # Small fast models
    {"name": "llama3.2:1b", "size": "1B", "expected_speed": "very fast"},
    {"name": "llama3.2:3b", "size": "3B", "expected_speed": "fast"},

    # Medium models
    {"name": "qwen3:7b", "size": "7B", "expected_speed": "medium"},
    {"name": "llama3.1:8b", "size": "8B", "expected_speed": "medium"},

    # Larger models (comment out if too slow)
    {"name": "qwen3:14b", "size": "14B", "expected_speed": "slow"},
    # {"name": "llama3.1:70b", "size": "70B", "expected_speed": "very slow"},
]


class LLMBenchmark:
    """Benchmark LLM models for two-step schema generation."""

    def __init__(self):
        self.results: List[Dict[str, Any]] = []

    def test_model(self, model_config: Dict[str, str]) -> Dict[str, Any]:
        """Test a single model."""
        model_name = model_config["name"]
        print(f"\n{'='*80}")
        print(f"Testing: {model_name} ({model_config['size']} parameters)")
        print(f"Expected Speed: {model_config['expected_speed']}")
        print(f"{'='*80}")

        # Set model
        os.environ["OLLAMA_MODEL"] = model_name

        try:
            # Create service
            service = StructuredOutputService(
                use_ollama=True,
                enable_caching=False  # Disable cache for fair comparison
            )

            # Test 1: Schema Generation
            print("\n[1/3] Schema Generation...")
            schema_start = time.time()

            schema_result = service.generate_schema_from_content(
                content=TEST_CONTENT,
                query="Extract RAG pattern information as a table",
                schema_type="table",
                use_cache=False
            )

            schema_time = time.time() - schema_start
            schema_success = schema_result.get("success", False)

            print(f"   ✅ Time: {schema_time:.2f}s")
            print(f"   Success: {schema_success}")

            if not schema_success:
                print(f"   ❌ Error: {schema_result.get('error', 'Unknown')}")
                return {
                    "model": model_name,
                    "size": model_config["size"],
                    "schema_time": schema_time,
                    "schema_success": False,
                    "extraction_time": 0,
                    "extraction_success": False,
                    "total_time": schema_time,
                    "error": schema_result.get("error", "Unknown")
                }

            # Test 2: Data Extraction
            print("\n[2/3] Data Extraction...")
            extract_start = time.time()

            extraction_result = service.extract_data_with_schema(
                content=TEST_CONTENT,
                schema=schema_result["schema"],
                query="Extract RAG pattern information",
                output_format="json",
                validate=False
            )

            extract_time = time.time() - extract_start
            extract_success = extraction_result.get("success", False)

            print(f"   ✅ Time: {extract_time:.2f}s")
            print(f"   Success: {extract_success}")

            # Test 3: Quality Check
            print("\n[3/3] Quality Check...")
            quality_score = self._check_quality(extraction_result)
            print(f"   Quality Score: {quality_score}/10")

            # Summary
            total_time = schema_time + extract_time
            print(f"\n📊 Summary for {model_name}:")
            print(f"   Schema Generation: {schema_time:.2f}s")
            print(f"   Data Extraction:   {extract_time:.2f}s")
            print(f"   Total Time:        {total_time:.2f}s")
            print(f"   Quality Score:     {quality_score}/10")

            result = {
                "model": model_name,
                "size": model_config["size"],
                "schema_time": schema_time,
                "schema_success": schema_success,
                "extraction_time": extract_time,
                "extraction_success": extract_success,
                "total_time": total_time,
                "quality_score": quality_score,
                "schema_result": schema_result if schema_success else None,
                "extraction_result": extraction_result if extract_success else None
            }

            self.results.append(result)
            return result

        except Exception as e:
            print(f"\n❌ Model {model_name} failed: {e}")
            return {
                "model": model_name,
                "size": model_config["size"],
                "schema_time": 0,
                "schema_success": False,
                "extraction_time": 0,
                "extraction_success": False,
                "total_time": 0,
                "error": str(e)
            }

    def _check_quality(self, extraction_result: Dict[str, Any]) -> int:
        """
        Check quality of extracted data (0-10 scale).

        Checks for:
        - Data extracted (not schema)
        - Contains expected patterns
        - Reasonable structure
        """
        if not extraction_result.get("success"):
            return 0

        data = extraction_result.get("data", {})
        score = 0

        # Check 1: Is it actual data (not schema definition)?
        if isinstance(data, dict):
            # Schema definitions have these keys
            if "properties" in data and "type" in data:
                print("      ⚠️  Looks like schema definition (not data)")
                return 1
            score += 3

        # Check 2: Contains pattern names?
        data_str = json.dumps(data).lower()
        patterns = ["basic rag", "advanced rag", "self-rag", "streaming rag"]
        found_patterns = sum(1 for p in patterns if p in data_str)
        score += min(found_patterns, 4)  # Max 4 points

        # Check 3: Has structured data (arrays, objects)?
        if isinstance(data, dict):
            if any(isinstance(v, (list, dict)) for v in data.values()):
                score += 2
        elif isinstance(data, list) and len(data) > 0:
            score += 2

        # Check 4: Reasonable size (not too small)
        if len(data_str) > 100:
            score += 1

        return min(score, 10)

    def print_comparison_table(self):
        """Print comparison table of all results."""
        print("\n" + "="*100)
        print("BENCHMARK RESULTS - COMPARISON TABLE")
        print("="*100)
        print(f"{'Model':<20} {'Size':<8} {'Schema':<10} {'Extract':<10} {'Total':<10} {'Quality':<10} {'Status'}")
        print("-"*100)

        for result in self.results:
            model = result["model"]
            size = result["size"]
            schema_time = f"{result['schema_time']:.2f}s" if result['schema_success'] else "FAIL"
            extract_time = f"{result['extraction_time']:.2f}s" if result['extraction_success'] else "FAIL"
            total_time = f"{result['total_time']:.2f}s" if result.get('total_time', 0) > 0 else "FAIL"
            quality = f"{result.get('quality_score', 0)}/10" if result.get('quality_score') else "N/A"

            if result['schema_success'] and result['extraction_success']:
                status = "✅ PASS"
            elif result.get('error'):
                status = f"❌ {result['error'][:20]}"
            else:
                status = "❌ FAIL"

            print(f"{model:<20} {size:<8} {schema_time:<10} {extract_time:<10} {total_time:<10} {quality:<10} {status}")

        print("-"*100)

        # Find best model
        successful = [r for r in self.results if r['schema_success'] and r['extraction_success']]
        if successful:
            fastest = min(successful, key=lambda x: x['total_time'])
            best_quality = max(successful, key=lambda x: x.get('quality_score', 0))

            print(f"\n🏆 FASTEST: {fastest['model']} ({fastest['total_time']:.2f}s total)")
            print(f"🏆 BEST QUALITY: {best_quality['model']} (score: {best_quality.get('quality_score', 0)}/10)")

            # Recommend best balance
            for r in successful:
                r['balance_score'] = (r.get('quality_score', 0) / 10) - (r['total_time'] / 30)
            best_balance = max(successful, key=lambda x: x.get('balance_score', 0))
            print(f"🏆 BEST BALANCE: {best_balance['model']}")

        print("="*100)

    def save_detailed_results(self, output_file: str = "benchmark_results.json"):
        """Save detailed results to JSON file."""
        output_path = Path(__file__).parent.parent / output_file

        # Remove large objects for cleaner JSON
        clean_results = []
        for r in self.results:
            clean = r.copy()
            clean.pop('schema_result', None)
            clean.pop('extraction_result', None)
            clean_results.append(clean)

        with open(output_path, 'w') as f:
            json.dump(clean_results, f, indent=2)

        print(f"\n💾 Detailed results saved to: {output_path}")


def main():
    """Run benchmark."""
    print("="*100)
    print("LLM MODEL BENCHMARK - Two-Step Schema Generation & Data Extraction")
    print("="*100)
    print(f"\nTest Content Size: {len(TEST_CONTENT)} characters")
    print(f"Models to Test: {len(MODELS_TO_TEST)}")
    print(f"\nThis will test each model's ability to:")
    print("  1. Generate a schema from document content")
    print("  2. Extract data using that schema")
    print("  3. Quality of extracted data")

    input("\nPress Enter to start benchmark (or Ctrl+C to cancel)...")

    benchmark = LLMBenchmark()

    # Test each model
    for i, model_config in enumerate(MODELS_TO_TEST, 1):
        print(f"\n\n{'#'*100}")
        print(f"# Model {i}/{len(MODELS_TO_TEST)}")
        print(f"{'#'*100}")

        try:
            benchmark.test_model(model_config)
        except KeyboardInterrupt:
            print("\n\n⚠️  Benchmark interrupted by user")
            break
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            continue

    # Print comparison
    benchmark.print_comparison_table()

    # Save results
    benchmark.save_detailed_results()

    print("\n✅ Benchmark complete!")


if __name__ == "__main__":
    main()
