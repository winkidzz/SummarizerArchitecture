#!/usr/bin/env python3
"""
Run Ragas evaluation on RAG system using local Ollama models.

Usage:
    python scripts/run_ragas_eval.py
    python scripts/run_ragas_eval.py --eval-file ragas_eval_set.json
    python scripts/run_ragas_eval.py --model gemma3:4b
"""

import argparse
import json
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from document_store.storage.vector_store import VectorStore
from document_store.search.rag_query import RAGQueryInterface
from document_store.evaluation.ragas_evaluator import (
    RagasEvaluator,
    RagasMetrics,
    evaluate_batch
)


def load_eval_set(eval_file: str) -> dict:
    """Load evaluation dataset from JSON file."""
    eval_path = Path(__file__).parent.parent / eval_file
    with open(eval_path) as f:
        return json.load(f)


def run_rag_system(rag: RAGQueryInterface, query: str, n_results: int = 5) -> dict:
    """Run RAG system and return response + contexts."""
    result = rag.query_patterns(query=query, n_results=n_results)

    # Extract contexts (document content)
    contexts = [r["content"] for r in result.get("results", [])]

    # Build a simple response (in real scenario, LLM would synthesize this)
    # For now, just concatenate top contexts
    response = "\n\n".join([
        f"Based on the documentation: {ctx[:300]}..."
        for ctx in contexts[:3]
    ])

    return {
        "response": response,
        "contexts": contexts,
        "metadata": result
    }


def main():
    parser = argparse.ArgumentParser(description="Run Ragas evaluation")
    parser.add_argument(
        "--eval-file",
        default="ragas_eval_set.json",
        help="Evaluation dataset file"
    )
    parser.add_argument(
        "--model",
        default="qwen3:14b",
        help="Ollama model to use as judge"
    )
    parser.add_argument(
        "--ollama-url",
        default="http://localhost:11434",
        help="Ollama API base URL"
    )
    parser.add_argument(
        "--output",
        default="ragas_results.json",
        help="Output file for results"
    )

    args = parser.parse_args()

    print("=" * 70)
    print("RAGAS EVALUATION - RAG System Quality Assessment")
    print("=" * 70)
    print(f"Evaluation file: {args.eval_file}")
    print(f"Judge model: {args.model}")
    print(f"Ollama URL: {args.ollama_url}")
    print("=" * 70)

    # Load evaluation dataset
    print("\n📋 Loading evaluation dataset...")
    eval_data = load_eval_set(args.eval_file)
    test_cases_raw = eval_data["test_cases"]
    print(f"✓ Loaded {len(test_cases_raw)} test cases")

    # Initialize RAG system
    print("\n🔧 Initializing RAG system...")
    vector_store = VectorStore(
        persist_directory="data/chroma_db",
        collection_name="architecture_patterns"
    )
    rag = RAGQueryInterface(vector_store=vector_store)
    print("✓ RAG system ready")

    # Initialize Ragas evaluator
    print(f"\n⚖️  Initializing Ragas evaluator (model: {args.model})...")
    evaluator = RagasEvaluator(
        model=args.model,
        base_url=args.ollama_url
    )
    print("✓ Evaluator ready")

    # Run RAG system on each test case
    print(f"\n🚀 Running RAG system on {len(test_cases_raw)} queries...")
    test_cases = []

    for i, case in enumerate(test_cases_raw, 1):
        print(f"\n[{i}/{len(test_cases_raw)}] Query: {case['query'][:60]}...")

        start = time.time()
        rag_result = run_rag_system(rag, case["query"])
        elapsed = time.time() - start

        print(f"  ✓ Retrieved {len(rag_result['contexts'])} contexts ({elapsed:.2f}s)")

        test_cases.append({
            "id": case.get("id", f"test_{i}"),
            "query": case["query"],
            "response": rag_result["response"],
            "contexts": rag_result["contexts"],
            "reference": case.get("reference_answer")
        })

    # Run Ragas evaluation
    print("\n" + "=" * 70)
    print("🔍 EVALUATING WITH RAGAS METRICS")
    print("=" * 70)
    print("This will take 5-10 seconds per test case...")
    print()

    metrics = [
        RagasMetrics.FAITHFULNESS,
        RagasMetrics.ANSWER_RELEVANCY,
        RagasMetrics.CONTEXT_PRECISION,
        RagasMetrics.CONTEXT_RECALL
    ]

    eval_start = time.time()
    results = evaluate_batch(evaluator, test_cases, metrics=metrics)
    eval_elapsed = time.time() - eval_start

    # Display results
    print("\n" + "=" * 70)
    print("📊 RESULTS")
    print("=" * 70)

    for result in results["results"]:
        print(f"\n[{result['test_id']}] {result['query'][:60]}...")
        print(f"  Overall Score: {result['overall_score']:.3f}")
        for metric, score in result["scores"].items():
            if score is not None:
                print(f"    {metric:20s}: {score:.3f}")
            else:
                print(f"    {metric:20s}: N/A (no reference)")

    # Aggregate statistics
    print("\n" + "=" * 70)
    print("📈 AGGREGATE STATISTICS")
    print("=" * 70)
    aggregate = results["aggregate"]

    print(f"\n  Overall Average: {aggregate['overall']:.3f}")
    print("\n  Metric Averages:")
    for metric in metrics:
        if metric in aggregate:
            print(f"    {metric:20s}: {aggregate[metric]:.3f}")

    print(f"\n  Total test cases: {results['num_cases']}")
    print(f"  Total evaluation time: {eval_elapsed:.1f}s")
    print(f"  Average time per case: {eval_elapsed / results['num_cases']:.1f}s")

    # Save results
    output_path = Path(__file__).parent.parent / args.output
    with open(output_path, "w") as f:
        json.dump({
            "eval_dataset": args.eval_file,
            "judge_model": args.model,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "results": results["results"],
            "aggregate": aggregate,
            "metadata": {
                "num_cases": results["num_cases"],
                "total_time": eval_elapsed,
                "avg_time_per_case": eval_elapsed / results["num_cases"]
            }
        }, f, indent=2)

    print(f"\n✓ Results saved to: {output_path}")
    print("\n" + "=" * 70)

    return 0 if aggregate["overall"] >= 0.7 else 1


if __name__ == "__main__":
    sys.exit(main())
