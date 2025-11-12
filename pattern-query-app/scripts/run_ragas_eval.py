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
import logging
import os
import sys
import time
from pathlib import Path
from typing import Optional

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    # Load .env from project root (parent of scripts directory)
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        logger = logging.getLogger(__name__)
        logger.debug(f"Loaded environment variables from {env_path}")
except ImportError:
    pass  # python-dotenv not installed, skip

logging.basicConfig(level=logging.WARNING)  # Only show warnings/errors
logger = logging.getLogger(__name__)

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from document_store.storage.vector_store import VectorStore
from document_store.search.rag_query import RAGQueryInterface
from document_store.agents.ollama_agent import OllamaAgent

# Import evaluators - try real Ragas first, then fall back to custom
try:
    from document_store.evaluation.ragas_real import (
        RagasRealEvaluator,
        evaluate_batch as ragas_real_evaluate_batch,
    )
    RAGAS_REAL_AVAILABLE = True
except ImportError:
    RAGAS_REAL_AVAILABLE = False
    RagasRealEvaluator = None
    ragas_real_evaluate_batch = None

from document_store.evaluation.ragas_evaluator import (
    RagasEvaluator as OllamaEvaluator,
    RagasMetrics,
    evaluate_batch as ollama_evaluate_batch,
)

try:
    from document_store.evaluation.gemini_evaluator import (
        GeminiEvaluator,
        evaluate_batch as gemini_evaluate_batch,
    )
    GEMINI_CUSTOM_AVAILABLE = True
except ImportError:
    GEMINI_CUSTOM_AVAILABLE = False
    GeminiEvaluator = None
    gemini_evaluate_batch = None


def load_eval_set(eval_file: str) -> dict:
    """Load evaluation dataset from JSON file."""
    eval_path = Path(__file__).parent.parent / eval_file
    with open(eval_path) as f:
        return json.load(f)


def run_rag_system(
    rag: RAGQueryInterface, 
    query: str, 
    n_results: int = 5,
    ollama_agent: Optional[OllamaAgent] = None
) -> dict:
    """Run RAG system and return response + contexts."""
    result = rag.query_patterns(query=query, n_results=n_results)

    # Extract contexts (document content)
    contexts = [r["content"] for r in result.get("results", [])]

    # Generate response using LLM if available, otherwise use simple concatenation
    if ollama_agent and contexts:
        try:
            # Use LLM to generate proper response
            system_prompt = (
                "You are an expert in AI architecture patterns and healthcare summarization. "
                "Answer questions based on the provided context documents. "
                "Format your responses according to the user's request (CSV, tables, etc.). "
                "If the answer is not in the context, say so explicitly."
            )
            rag_response = ollama_agent.build_rag_response(
                query=query,
                context_documents=contexts,
                system_prompt=system_prompt
            )
            response = rag_response.get("answer", "")
        except Exception as e:
            logger.warning(f"LLM response generation failed: {e}. Using fallback.")
            # Fallback to simple concatenation
            response = "\n\n".join([
                f"Based on the documentation: {ctx[:500]}..."
                for ctx in contexts[:3]
            ])
    else:
        # Fallback: simple concatenation
        response = "\n\n".join([
            f"Based on the documentation: {ctx[:500]}..."
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
        help="Model to use as judge (Ollama model name or Gemini model like 'gemini-2.5-flash')"
    )
    parser.add_argument(
        "--ollama-url",
        default="http://192.168.1.204:11434",
        help="Ollama API base URL (only used for Ollama models, default: http://192.168.1.204:11434)"
    )
    parser.add_argument(
        "--llm-type",
        default="auto",
        choices=["auto", "ollama", "gemini"],
        help="LLM type: 'auto' (detect from model name), 'ollama', or 'gemini' (default: auto)"
    )
    parser.add_argument(
        "--output",
        default="ragas_results.json",
        help="Output file for results"
    )
    parser.add_argument(
        "--response-model",
        default=None,
        help="Ollama model to use for generating responses (default: same as judge model)"
    )
    parser.add_argument(
        "--no-llm-response",
        action="store_true",
        help="Disable LLM response generation (use simple concatenation)"
    )

    args = parser.parse_args()

    # Read configuration from environment variables
    use_ollama_eval = os.getenv("USE_OLLAMA_EVAL", "false").lower() == "true"
    use_real_ragas = os.getenv("USE_REAL_RAGAS", "false").lower() == "true"

    # Determine LLM type for display
    if args.llm_type == "auto":
        if use_ollama_eval:
            detected_type = "Ollama"
        else:
            detected_type = "Gemini"
    else:
        detected_type = args.llm_type.capitalize()
    
    print("=" * 70)
    print("RAGAS EVALUATION - RAG System Quality Assessment")
    print("=" * 70)
    print(f"Evaluation file: {args.eval_file}")
    print(f"Judge model: {args.model} ({detected_type})")
    if args.llm_type != "gemini":
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
    
    # Initialize LLM for response generation (if enabled)
    ollama_agent = None
    if not args.no_llm_response:
        response_model = args.response_model or args.model
        try:
            print(f"\n🤖 Initializing response generator (model: {response_model})...")
            ollama_agent = OllamaAgent(
                model=response_model,
                base_url=args.ollama_url
            )
            print("✓ Response generator ready")
        except Exception as e:
            print(f"⚠️  Could not initialize response generator: {e}")
            print("   Falling back to simple concatenation")
            ollama_agent = None

    # Initialize Ragas evaluator based on environment configuration
    print("\n⚖️  Initializing evaluator...")
    print(f"   Configuration: USE_OLLAMA_EVAL={use_ollama_eval}, USE_REAL_RAGAS={use_real_ragas}")

    if use_ollama_eval:
        # Use Ollama evaluator (custom implementation only)
        if use_real_ragas:
            print("✗ Error: Real Ragas with Ollama is not implemented")
            print("  Set USE_REAL_RAGAS=false to use custom Ollama evaluator")
            return 1

        print(f"   Using custom Ollama evaluator (model: {args.model})...")
        evaluator = OllamaEvaluator(
            model=args.model,
            base_url=args.ollama_url
        )
        evaluate_batch_func = ollama_evaluate_batch
        print("✓ Ollama evaluator ready")

    else:
        # Use Gemini evaluator
        if use_real_ragas:
            # Use Real Ragas library with Gemini
            if not RAGAS_REAL_AVAILABLE:
                print("✗ Error: Real Ragas library not available")
                print("  Install with: pip install ragas")
                print("  OR set USE_REAL_RAGAS=false to use custom implementation")
                return 1

            print(f"   Using REAL Ragas evaluator with Gemini (model: {args.model})...")
            try:
                evaluator = RagasRealEvaluator(model=args.model, llm_type="gemini")
                evaluate_batch_func = ragas_real_evaluate_batch
                print("✓ Real Ragas evaluator ready")
            except Exception as e:
                print(f"✗ Failed to initialize Real Ragas: {e}")
                print("  Set USE_REAL_RAGAS=false to use custom implementation")
                return 1

        else:
            # Use custom Gemini evaluator
            if not GEMINI_CUSTOM_AVAILABLE:
                print("✗ Error: Custom Gemini evaluator not available")
                print("  Install with: pip install google-generativeai")
                return 1

            print(f"   Using custom Gemini evaluator (model: {args.model})...")
            try:
                evaluator = GeminiEvaluator(model=args.model)
                evaluate_batch_func = gemini_evaluate_batch
                print("✓ Custom Gemini evaluator ready")
            except Exception as e:
                print(f"✗ Failed to initialize Gemini evaluator: {e}")
                print("  Make sure GEMINI_API_KEY is set in your .env file")
                return 1

    # Run RAG system on each test case
    print(f"\n🚀 Running RAG system on {len(test_cases_raw)} queries...")
    test_cases = []

    for i, case in enumerate(test_cases_raw, 1):
        print(f"\n[{i}/{len(test_cases_raw)}] Query: {case['query'][:60]}...")

        # Use more results for queries that need complete datasets
        n_results = case.get("n_results", 5)
        if "complete" in case["query"].lower() or "all" in case["query"].lower():
            n_results = max(n_results, 20)  # Get more chunks for "complete" queries

        start = time.time()
        rag_result = run_rag_system(rag, case["query"], n_results=n_results, ollama_agent=ollama_agent)
        elapsed = time.time() - start

        response_method = "LLM-generated" if ollama_agent else "concatenated"
        print(f"  ✓ Retrieved {len(rag_result['contexts'])} contexts, {response_method} response ({elapsed:.2f}s)")

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

    # Metrics list - use string names for compatibility
    metrics = [
        "faithfulness",
        "answer_relevancy",
        "context_precision",
        "context_recall"
    ]

    eval_start = time.time()
    results = evaluate_batch_func(evaluator, test_cases, metrics=metrics)
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
