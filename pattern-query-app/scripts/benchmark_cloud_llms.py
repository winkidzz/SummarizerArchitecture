#!/usr/bin/env python3
"""
Benchmark CLOUD LLM models (Gemini, Claude via API) for schema generation.

Compares cloud providers for:
- Speed
- Quality
- Cost per operation
- Two-step performance
"""
import sys
import os
import time
import json
from pathlib import Path
from typing import Dict, Any, List

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from document_store.formatting import StructuredOutputService

# Test content (same as Ollama benchmark)
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
"""

# Cloud models to test
CLOUD_MODELS = [
    # Google Gemini
    {
        "name": "gemini-2.0-flash-exp",
        "provider": "Google",
        "cost_per_1k_tokens": 0.0001,  # Very cheap
        "use_ollama": False,
        "requires_api_key": "GEMINI_API_KEY"
    },
    {
        "name": "gemini-1.5-pro",
        "provider": "Google",
        "cost_per_1k_tokens": 0.0025,
        "use_ollama": False,
        "requires_api_key": "GEMINI_API_KEY"
    },

    # Add more providers as needed
    # {
    #     "name": "gpt-4-turbo",
    #     "provider": "OpenAI",
    #     "cost_per_1k_tokens": 0.01,
    #     "use_ollama": False,
    #     "requires_api_key": "OPENAI_API_KEY"
    # },
]


def check_api_keys() -> Dict[str, bool]:
    """Check which API keys are available."""
    keys = {
        "GEMINI_API_KEY": bool(os.getenv("GEMINI_API_KEY")),
        "OPENAI_API_KEY": bool(os.getenv("OPENAI_API_KEY")),
        "ANTHROPIC_API_KEY": bool(os.getenv("ANTHROPIC_API_KEY")),
    }
    return keys


def estimate_tokens(text: str) -> int:
    """Rough token estimate (1 token ≈ 4 characters)."""
    return len(text) // 4


def benchmark_cloud_model(model_config: Dict[str, Any]) -> Dict[str, Any]:
    """Benchmark a single cloud model."""
    model_name = model_config["name"]
    provider = model_config["provider"]

    print(f"\n{'='*80}")
    print(f"Testing: {model_name} ({provider})")
    print(f"Cost per 1K tokens: ${model_config['cost_per_1k_tokens']}")
    print(f"{'='*80}")

    # Check API key
    api_key_name = model_config["requires_api_key"]
    if not os.getenv(api_key_name):
        print(f"❌ Skipping - {api_key_name} not set")
        return {
            "model": model_name,
            "provider": provider,
            "error": f"{api_key_name} not set",
            "skipped": True
        }

    try:
        # Create service
        service = StructuredOutputService(
            model_name=model_name,
            use_ollama=model_config["use_ollama"],
            enable_caching=False
        )

        # Test 1: Schema Generation
        print("\n[1/2] Schema Generation...")
        schema_start = time.time()

        schema_result = service.generate_schema_from_content(
            content=TEST_CONTENT,
            query="Extract RAG pattern information as a table",
            schema_type="table",
            use_cache=False
        )

        schema_time = time.time() - schema_start
        schema_success = schema_result.get("success", False)

        print(f"   Time: {schema_time:.2f}s")
        print(f"   Success: {schema_success}")

        if not schema_success:
            return {
                "model": model_name,
                "provider": provider,
                "schema_time": schema_time,
                "schema_success": False,
                "error": schema_result.get("error", "Unknown")
            }

        # Test 2: Data Extraction
        print("\n[2/2] Data Extraction...")
        extract_start = time.time()

        extraction_result = service.extract_data_with_schema(
            content=TEST_CONTENT,
            schema=schema_result["schema"],
            output_format="json",
            validate=False
        )

        extract_time = time.time() - extract_start
        extract_success = extraction_result.get("success", False)

        print(f"   Time: {extract_time:.2f}s")
        print(f"   Success: {extract_success}")

        # Calculate cost estimate
        total_tokens = estimate_tokens(TEST_CONTENT) * 2  # Rough estimate
        estimated_cost = (total_tokens / 1000) * model_config["cost_per_1k_tokens"]

        total_time = schema_time + extract_time

        print(f"\n📊 Summary:")
        print(f"   Total Time: {total_time:.2f}s")
        print(f"   Estimated Cost: ${estimated_cost:.6f}")

        return {
            "model": model_name,
            "provider": provider,
            "schema_time": schema_time,
            "schema_success": schema_success,
            "extraction_time": extract_time,
            "extraction_success": extract_success,
            "total_time": total_time,
            "estimated_cost": estimated_cost,
            "cost_per_1k": model_config["cost_per_1k_tokens"]
        }

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return {
            "model": model_name,
            "provider": provider,
            "error": str(e)
        }


def print_comparison(results: List[Dict[str, Any]]):
    """Print comparison table."""
    print("\n" + "="*100)
    print("CLOUD LLM BENCHMARK RESULTS")
    print("="*100)
    print(f"{'Model':<30} {'Provider':<10} {'Time':<10} {'Cost':<12} {'Status'}")
    print("-"*100)

    for r in results:
        if r.get("skipped"):
            print(f"{r['model']:<30} {r['provider']:<10} {'N/A':<10} {'N/A':<12} ⚠️  SKIPPED")
        elif r.get("error"):
            print(f"{r['model']:<30} {r['provider']:<10} {'N/A':<10} {'N/A':<12} ❌ ERROR")
        elif r.get("schema_success") and r.get("extraction_success"):
            time_str = f"{r['total_time']:.2f}s"
            cost_str = f"${r['estimated_cost']:.6f}"
            print(f"{r['model']:<30} {r['provider']:<10} {time_str:<10} {cost_str:<12} ✅ PASS")
        else:
            print(f"{r['model']:<30} {r['provider']:<10} {'FAIL':<10} {'N/A':<12} ❌ FAIL")

    print("="*100)


def main():
    """Run cloud benchmark."""
    print("="*100)
    print("CLOUD LLM BENCHMARK - Two-Step Schema Generation")
    print("="*100)

    # Check API keys
    print("\n🔑 Checking API Keys...")
    keys = check_api_keys()
    for key_name, available in keys.items():
        status = "✅ Available" if available else "❌ Not set"
        print(f"   {key_name}: {status}")

    available_keys = [k for k, v in keys.items() if v]
    if not available_keys:
        print("\n❌ No API keys found. Set at least one:")
        print("   export GEMINI_API_KEY='your-key'")
        print("   export OPENAI_API_KEY='your-key'")
        return

    # Filter models based on available keys
    testable_models = [
        m for m in CLOUD_MODELS
        if os.getenv(m["requires_api_key"])
    ]

    if not testable_models:
        print("\n❌ No testable models (no matching API keys)")
        return

    print(f"\n📋 Will test {len(testable_models)} models")

    input("\nPress Enter to start (will cost ~$0.001)...")

    results = []
    for model_config in testable_models:
        result = benchmark_cloud_model(model_config)
        results.append(result)

    # Print comparison
    print_comparison(results)

    # Save results
    output_path = Path(__file__).parent.parent / "benchmark_cloud_results.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n💾 Results saved to: {output_path}")


if __name__ == "__main__":
    main()
