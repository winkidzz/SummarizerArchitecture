#!/usr/bin/env python3
"""
Run simple evaluation set against the pattern query app.
"""

import json
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from document_store.storage.vector_store import VectorStore
from document_store.search.rag_query import RAGQueryInterface


def run_eval(eval_file: str = "simple_eval_set.json"):
    """Run evaluation tests."""

    # Load eval set
    eval_path = Path(__file__).parent.parent / eval_file
    with open(eval_path) as f:
        eval_data = json.load(f)

    print(f"Running: {eval_data['name']}")
    print(f"Tests: {len(eval_data['test_cases'])}")
    print("=" * 60)

    # Initialize RAG interface directly (avoid orchestrator dependencies)
    vector_store = VectorStore(
        persist_directory="data/chroma_db",
        collection_name="architecture_patterns"
    )
    rag = RAGQueryInterface(vector_store=vector_store)

    results = []

    for i, test in enumerate(eval_data["test_cases"], 1):
        test_id = test["id"]
        query = test["query"]
        expected = test["expected"]

        print(f"\n[{i}/{len(eval_data['test_cases'])}] Test: {test_id}")
        print(f"Query: {query}")
        print(f"Expected: {expected}")

        start = time.time()
        try:
            result = rag.query_patterns(query=query, n_results=5)
            elapsed = time.time() - start

            # Get results from RAG
            query_results = result.get("results", [])

            # Simple validation: got results back
            passed = len(query_results) > 0

            # Print first result
            if query_results:
                first_doc = query_results[0]["content"][:150]
                print(f"✓ Pass ({elapsed:.2f}s): {len(query_results)} docs")
                print(f"  First doc: {first_doc}...")
            else:
                print(f"✗ Fail ({elapsed:.2f}s): No documents retrieved")

            results.append({
                "test_id": test_id,
                "query": query,
                "passed": passed,
                "elapsed": elapsed,
                "documents_count": len(query_results)
            })

        except Exception as e:
            elapsed = time.time() - start
            print(f"✗ Error ({elapsed:.2f}s): {e}")
            results.append({
                "test_id": test_id,
                "query": query,
                "passed": False,
                "elapsed": elapsed,
                "error": str(e)
            })

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    passed = sum(1 for r in results if r["passed"])
    total = len(results)
    avg_time = sum(r["elapsed"] for r in results) / total

    print(f"Passed: {passed}/{total} ({passed/total*100:.1f}%)")
    print(f"Average time: {avg_time:.2f}s")

    # Save results
    results_file = Path(__file__).parent.parent / "eval_results.json"
    with open(results_file, "w") as f:
        json.dump({
            "eval_name": eval_data["name"],
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "summary": {
                "passed": passed,
                "total": total,
                "pass_rate": passed/total,
                "avg_time": avg_time
            },
            "results": results
        }, f, indent=2)

    print(f"\nResults saved to: {results_file}")

    return passed == total


if __name__ == "__main__":
    success = run_eval()
    sys.exit(0 if success else 1)
